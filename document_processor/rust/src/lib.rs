use calamine::{open_workbook, DataType, Range, Reader, Xlsx};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::path::PathBuf;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ExcelParserError {
    #[error("Failed to open Excel file: {0}")]
    OpenError(#[from] calamine::Error),
    
    #[error("Sheet not found: {0}")]
    SheetNotFound(String),
    
    #[error("Failed to parse Excel content: {0}")]
    ParseError(String),
}

#[pyclass]
struct RustExcelParser {}

#[pymethods]
impl RustExcelParser {
    #[new]
    fn new() -> Self {
        RustExcelParser {}
    }

    /// Parse an Excel file from bytes and return a dictionary of sheets
    #[pyo3(text_signature = "(content, /)")]
    fn parse_excel<'py>(&self, py: Python<'py>, content: &[u8]) -> PyResult<&'py PyDict> {
        let result = PyDict::new(py);
        
        // Create a temporary file to write the content
        let temp_dir = tempfile::tempdir().map_err(|e| {
            PyValueError::new_err(format!("Failed to create temporary directory: {}", e))
        })?;
        
        let temp_path = temp_dir.path().join("temp.xlsx");
        std::fs::write(&temp_path, content).map_err(|e| {
            PyValueError::new_err(format!("Failed to write temporary file: {}", e))
        })?;
        
        // Open the Excel file
        let mut workbook: Xlsx<_> = match open_workbook(&temp_path) {
            Ok(wb) => wb,
            Err(e) => return Err(PyValueError::new_err(format!("Failed to open Excel file: {}", e))),
        };
        
        // Process each sheet
        for sheet_name in workbook.sheet_names().to_owned() {
            let sheet = match workbook.worksheet_range(&sheet_name) {
                Ok(range) => range,
                Err(e) => {
                    return Err(PyValueError::new_err(format!(
                        "Error reading sheet {}: {}", sheet_name, e
                    )))
                }
            };
            
            let sheet_data = self.process_sheet(py, &sheet)?;
            result.set_item(sheet_name, sheet_data)?;
        }
        
        Ok(result)
    }
    
    /// Extract questions from sheets
    #[pyo3(text_signature = "(sheets, /)")]
    fn extract_questions<'py>(&self, py: Python<'py>, sheets: &PyDict) -> PyResult<&'py PyList> {
        let questions = PyList::empty(py);
        
        for (sheet_name, sheet_data) in sheets.iter() {
            let sheet_data = sheet_data.downcast::<PyList>()?;
            
            for (row_idx, row) in sheet_data.iter().enumerate() {
                let row = row.downcast::<PyDict>()?;
                
                // Look for cells that appear to be questions
                for (col_key, cell_value) in row.iter() {
                    let cell_str = cell_value.to_string();
                    
                    // Simple heuristic: cells ending with ? are likely questions
                    // In a real implementation, we'd use more sophisticated detection
                    if cell_str.trim().ends_with("?") || 
                       cell_str.to_lowercase().contains("question") {
                        let question_dict = PyDict::new(py);
                        question_dict.set_item("sheet", sheet_name)?;
                        question_dict.set_item("row", row_idx)?;
                        question_dict.set_item("column", col_key)?;
                        question_dict.set_item("text", cell_str)?;
                        
                        questions.append(question_dict)?;
                    }
                }
            }
        }
        
        Ok(questions)
    }
    
    /// Get the structure of the Excel file (tabs, headers)
    #[pyo3(text_signature = "(sheets, /)")]
    fn get_structure<'py>(&self, py: Python<'py>, sheets: &PyDict) -> PyResult<&'py PyDict> {
        let structure = PyDict::new(py);
        
        for (sheet_name, sheet_data) in sheets.iter() {
            let sheet_data = sheet_data.downcast::<PyList>()?;
            
            // Get headers from the first row if available
            let headers = if !sheet_data.is_empty() {
                let first_row = sheet_data.get_item(0)?.downcast::<PyDict>()?;
                let headers_list = PyList::empty(py);
                
                for key in first_row.keys() {
                    headers_list.append(key)?;
                }
                
                headers_list
            } else {
                PyList::empty(py)
            };
            
            let sheet_info = PyDict::new(py);
            sheet_info.set_item("row_count", sheet_data.len())?;
            sheet_info.set_item("headers", headers)?;
            
            structure.set_item(sheet_name, sheet_info)?;
        }
        
        Ok(structure)
    }

    // Helper method to process a sheet into a list of dictionaries
    fn process_sheet<'py>(&self, py: Python<'py>, range: &Range<DataType>) -> PyResult<&'py PyList> {
        let rows = PyList::empty(py);
        
        // Get headers from the first row
        if range.height() == 0 {
            return Ok(rows);
        }
        
        let headers: Vec<String> = range.rows()
            .next()
            .unwrap()
            .iter()
            .map(|cell| match cell {
                DataType::String(s) => s.clone(),
                DataType::Int(i) => i.to_string(),
                DataType::Float(f) => f.to_string(),
                DataType::Bool(b) => b.to_string(),
                _ => "".to_string(),
            })
            .collect();
        
        // Process data rows
        for row_data in range.rows().skip(1) {
            let row_dict = PyDict::new(py);
            
            for (i, cell) in row_data.iter().enumerate() {
                if i >= headers.len() {
                    continue;
                }
                
                let header = &headers[i];
                if header.is_empty() {
                    continue;
                }
                
                // Convert cell to appropriate Python type
                let value = match cell {
                    DataType::String(s) => s.clone().to_object(py),
                    DataType::Int(i) => i.to_object(py),
                    DataType::Float(f) => f.to_object(py),
                    DataType::Bool(b) => b.to_object(py),
                    DataType::DateTime(d) => d.to_object(py),
                    DataType::Empty => py.None(),
                    DataType::Error(_) => py.None(),
                };
                
                row_dict.set_item(header, value)?;
            }
            
            rows.append(row_dict)?;
        }
        
        Ok(rows)
    }
}

#[pymodule]
fn excel_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustExcelParser>()?;
    Ok(())
}
