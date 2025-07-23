# Phase 2: Training Data Organization Guide

This guide covers the complete training data organization system for discipline-specific element detection in Construction AI.

## 🎯 Overview

Phase 2 establishes a robust foundation for collecting, organizing, and preprocessing training data for each discipline (Architectural, Structural, Civil, MEP). This is essential for building accurate ML models.

## 📁 Directory Structure

```
ml/data/
├── raw/                          # Original drawing files
│   ├── architectural/            # PDF, DWG, DXF files
│   ├── structural/              # PDF, DWG, DXF files
│   ├── civil/                   # PDF, DWG, DXF files
│   └── mep/                     # PDF, DWG, DXF files
├── processed/                    # Preprocessed images (1024x1024)
│   ├── architectural/
│   ├── structural/
│   ├── civil/
│   └── mep/
├── annotations/                  # Element annotations (JSON)
│   ├── architectural/
│   ├── structural/
│   ├── civil/
│   └── mep/
├── metadata/                     # Drawing metadata
│   ├── architectural/
│   ├── structural/
│   ├── civil/
│   └── mep/
└── datasets/                     # Training datasets
    ├── architectural/
    ├── structural/
    ├── civil/
    └── mep/
```

## 🛠️ Tools Overview

### 1. Data Collection Tool (`data_collector.py`)
- **TrainingDataCollector**: Manages drawing collection and organization
- **AnnotationManager**: Handles element annotations and validation

### 2. Data Preprocessing Tool (`data_preprocessor.py`)
- **DataPreprocessor**: Converts drawings to training-ready images
- **DataValidator**: Validates data quality and consistency

### 3. CLI Management Tool (`manage_data.py`)
- Command-line interface for all data operations
- Batch processing capabilities

## 📋 Step-by-Step Workflow

### Step 1: Install Dependencies
```bash
cd ml
pip install -r requirements.txt
```

### Step 2: Collect Training Data
```bash
# Collect a drawing file
python training/manage_data.py collect \
  --file-path /path/to/drawing.pdf \
  --discipline architectural \
  --metadata '{"project": "Sample Project", "scale": "1:100"}'

# Collect multiple drawings
for file in /path/to/drawings/*.pdf; do
  python training/manage_data.py collect \
    --file-path "$file" \
    --discipline architectural
done
```

### Step 3: Create Annotations
```bash
# Create annotation from template
python training/manage_data.py annotate \
  --drawing-id arch_abc123 \
  --discipline architectural

# Create annotation from custom elements file
python training/manage_data.py annotate \
  --drawing-id arch_abc123 \
  --discipline architectural \
  --elements-file custom_elements.json
```

### Step 4: Preprocess Drawings
```bash
# Preprocess a drawing
python training/manage_data.py preprocess \
  --drawing-id arch_abc123 \
  --discipline architectural \
  --target-size 1024x1024
```

### Step 5: Create Training Datasets
```bash
# Create dataset for a discipline
python training/manage_data.py dataset \
  --discipline architectural \
  --split-ratio 0.8
```

### Step 6: Validate Data
```bash
# Validate dataset
python training/manage_data.py validate \
  --discipline architectural

# Show statistics
python training/manage_data.py stats

# List drawings
python training/manage_data.py list \
  --discipline architectural
```

## 🏗️ Discipline-Specific Guidelines

### Architectural Drawings
**Target Elements:**
- Walls, doors, windows, rooms
- Furniture, fixtures, equipment
- Stairs, elevators, ramps
- Room labels, dimensions

**Data Requirements:**
- 100+ drawings minimum
- Various building types (residential, commercial, industrial)
- Different scales (1:50, 1:100, 1:200)
- Clear element boundaries

### Structural Drawings
**Target Elements:**
- Beams, columns, slabs
- Foundations, footings
- Reinforcement bars, stirrups
- Load calculations, dimensions

**Data Requirements:**
- 100+ drawings minimum
- Different structural systems
- Load-bearing elements clearly marked
- Material specifications

### Civil Drawings
**Target Elements:**
- Site plans, grading
- Drainage systems, utilities
- Roads, parking, landscaping
- Topographic contours

**Data Requirements:**
- 50+ drawings minimum
- Various site conditions
- Utility layouts
- Scale variations

### MEP Drawings
**Target Elements:**
- HVAC ducts, equipment
- Electrical panels, circuits
- Plumbing pipes, fixtures
- Fire protection systems

**Data Requirements:**
- 100+ drawings minimum
- Different system types
- Equipment specifications
- Clear system layouts

## 📊 Annotation Standards

### Element Annotation Format
```json
{
  "id": "unique_element_id",
  "type": "element_type",
  "bbox": [x1, y1, x2, y2],
  "confidence": 0.95,
  "properties": {
    "dimensions": "string",
    "material": "string",
    "specifications": "string"
  }
}
```

### Quality Control Checklist
- [ ] Minimum 2 annotators per drawing
- [ ] Inter-annotator agreement > 85%
- [ ] All elements properly bounded
- [ ] Properties accurately recorded
- [ ] No duplicate annotations
- [ ] Consistent naming conventions

## 🔄 Data Processing Pipeline

1. **Raw Collection** → `raw/`
   - Validate file formats
   - Generate unique IDs
   - Store metadata

2. **Preprocessing** → `processed/`
   - Convert to standard format
   - Resize to target dimensions
   - Apply image enhancement
   - Maintain aspect ratio

3. **Annotation** → `annotations/`
   - Mark element boundaries
   - Record properties
   - Validate annotations
   - Quality control

4. **Dataset Creation** → `datasets/`
   - Split train/validation
   - Generate configuration
   - Validate completeness

## 📈 Monitoring and Validation

### Data Quality Metrics
- **Completeness**: All drawings processed
- **Consistency**: Uniform annotation format
- **Accuracy**: Correct element identification
- **Balance**: Even distribution across types

### Validation Commands
```bash
# Check data quality
python training/manage_data.py validate --discipline architectural

# Monitor progress
python training/manage_data.py stats

# Verify annotations
python training/manage_data.py list --discipline architectural
```

## 🚀 Next Steps

After completing Phase 2:

1. **Phase 3**: Multi-Head Inference Strategy
   - Implement discipline-specific models
   - Add model switching logic
   - Improve detection accuracy

2. **Phase 4**: OCR → Element Mapping
   - Integrate PaddleOCR
   - Map text to elements
   - Enhance classification

3. **Phase 5**: Advanced ML Models
   - Replace geometric rules
   - Add confidence scoring
   - Implement active learning

## 📝 Best Practices

1. **Consistent Naming**: Use standardized element types
2. **Quality Over Quantity**: Focus on accurate annotations
3. **Regular Validation**: Check data quality frequently
4. **Version Control**: Track changes to annotations
5. **Documentation**: Maintain detailed metadata
6. **Backup**: Regular backups of training data

## 🆘 Troubleshooting

### Common Issues
1. **File Format Errors**: Check supported formats
2. **Annotation Validation**: Verify JSON structure
3. **Processing Failures**: Check file permissions
4. **Memory Issues**: Reduce batch sizes

### Support
- Check logs in `ml/training/` directory
- Validate data with CLI tools
- Review annotation templates
- Consult discipline-specific guidelines

---

**Phase 2 Complete!** 🎉 Your training data is now organized and ready for ML model development. 