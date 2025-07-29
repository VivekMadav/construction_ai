# Batch Upload & Analysis System

## Overview

The new batch upload and analysis system allows users to upload multiple drawings at once and perform cross-drawing reference analysis. This is essential for the cross-drawing reference functionality to work properly, as it needs all drawings to be available before it can analyze references between them.

## Key Features

### 1. Batch Upload Interface
- **Multiple File Selection**: Select multiple PDF files for each discipline
- **Discipline Organization**: Files are organized by discipline (Architectural, Structural, Civil, MEP)
- **Visual Feedback**: Shows selected file count and names
- **Progress Tracking**: Real-time upload progress and status

### 2. Cross-Drawing Analysis
- **Reference Detection**: Automatically detects references between drawings
- **Enhanced Measurements**: Combines measurements from multiple drawings
- **Notes Analysis**: Extracts and applies drawing notes and specifications
- **Confidence Scoring**: Provides confidence scores for cross-referenced measurements

### 3. Batch Analysis Options
- **Upload + Analyze**: Upload files and immediately analyze them together
- **Analyze Existing**: Re-analyze already uploaded drawings with cross-references
- **Selective Analysis**: Choose specific drawings for analysis

## How It Works

### Step 1: Batch Upload
1. Click "Show Batch Upload" in the project detail page
2. Select multiple PDF files for each discipline
3. Click "Upload & Analyze All"
4. System uploads all files first, then analyzes them together

### Step 2: Cross-Reference Analysis
1. System processes each drawing individually
2. Detects references to other drawings (section marks, detail references, etc.)
3. Matches elements across drawings
4. Combines measurements for improved accuracy
5. Applies drawing notes and specifications

### Step 3: Results
- **Cross-references found**: Number of references between drawings
- **Notes analyzed**: Number of drawings with notes extracted
- **Enhanced measurements**: More accurate measurements using multiple drawings
- **Confidence scores**: Reliability of cross-referenced measurements

## API Endpoints

### Batch Analysis
```http
POST /api/v1/enhanced-analysis/project/{project_id}/batch
```

**Request Body:**
```json
{
  "drawing_ids": [1, 2, 3, 4],
  "enable_cross_references": true,
  "enable_notes_analysis": true
}
```

**Response:**
```json
{
  "project_id": 1,
  "total_drawings": 4,
  "processed_drawings": 4,
  "cross_references_count": 12,
  "notes_analyzed_count": 3,
  "enable_cross_references": true,
  "enable_notes_analysis": true,
  "results": [...]
}
```

## Frontend Components

### Batch Upload UI
- **Collapsible Section**: Toggle batch upload interface
- **Multi-file Selection**: Select multiple files per discipline
- **Progress Indicators**: Show upload and analysis progress
- **Result Summary**: Display analysis results

### Analysis Controls
- **"Analyze All Drawings"**: Re-analyze existing drawings
- **"Upload & Analyze"**: Upload new files and analyze together
- **Status Indicators**: Show analysis progress and results

## Benefits

### 1. Improved Accuracy
- Cross-drawing references provide more complete information
- Measurements validated across multiple drawings
- Reduced errors from incomplete information

### 2. Better Workflow
- Upload all drawings at once instead of one-by-one
- Automatic cross-reference detection
- Comprehensive analysis in one step

### 3. Enhanced Features
- Drawing notes and specifications automatically applied
- Cross-drawing element matching
- Confidence scoring for measurements

## Usage Instructions

### For New Projects
1. Create a new project
2. Go to the project detail page
3. Click "Show Batch Upload"
4. Select all your drawing files by discipline
5. Click "Upload & Analyze All"
6. Wait for upload and analysis to complete
7. Review results and cross-references found

### For Existing Projects
1. Go to the project detail page
2. Click "Analyze All Drawings" to re-analyze existing drawings
3. Or upload additional drawings using batch upload
4. Review enhanced analysis results

## Technical Implementation

### Backend Changes
- **Enhanced Analysis API**: New batch analysis endpoint
- **Cross-Reference Processing**: Integrated into PDF processor
- **Notes Analysis**: Drawing notes extraction and application
- **Batch Upload Handling**: Multiple file upload processing

### Frontend Changes
- **Batch Upload UI**: New interface for multiple file selection
- **Analysis Controls**: Buttons for batch analysis
- **Progress Tracking**: Real-time status updates
- **Result Display**: Enhanced results with cross-reference information

## Error Handling

### Upload Errors
- Individual file upload failures are reported
- Failed uploads don't prevent other files from being processed
- Clear error messages for troubleshooting

### Analysis Errors
- Failed analysis doesn't affect other drawings
- Partial results are returned with error details
- Retry mechanisms for failed analysis

## Performance Considerations

### Large File Sets
- Files are uploaded sequentially to avoid overwhelming the server
- Analysis is performed after all uploads complete
- Progress indicators show current status

### Memory Management
- Large PDFs are processed efficiently
- Temporary files are cleaned up after processing
- Memory usage is optimized for batch operations

## Future Enhancements

### Planned Features
- **Parallel Processing**: Upload and analyze multiple files simultaneously
- **Background Processing**: Long-running analysis in background
- **Incremental Analysis**: Only analyze new or changed drawings
- **Advanced Cross-References**: More sophisticated reference detection

### Integration Opportunities
- **Version Control**: Track drawing versions and changes
- **Collaborative Analysis**: Multiple users working on same project
- **Advanced Reporting**: Enhanced reports with cross-reference information
- **Export Options**: Export cross-reference data for external tools 