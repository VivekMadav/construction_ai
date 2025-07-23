# Training Data Organization

This directory contains all training data organized by discipline for the Construction AI system.

## Directory Structure

```
ml/data/
├── raw/                          # Raw drawing files
│   ├── architectural/            # Original architectural drawings
│   ├── structural/              # Original structural drawings  
│   ├── civil/                   # Original civil drawings
│   └── mep/                     # Original MEP drawings
├── processed/                    # Preprocessed images
│   ├── architectural/
│   ├── structural/
│   ├── civil/
│   └── mep/
├── annotations/                  # Element annotations
│   ├── architectural/
│   ├── structural/
│   ├── civil/
│   └── mep/
├── metadata/                     # Drawing metadata
│   ├── architectural/
│   ├── structural/
│   ├── civil/
│   └── mep/
└── datasets/                     # Final training datasets
    ├── architectural/
    ├── structural/
    ├── civil/
    └── mep/
```

## Data Collection Guidelines

### Architectural Drawings
- **Element Types**: Walls, doors, windows, rooms, furniture, fixtures
- **File Formats**: PDF, DWG, DXF
- **Quality**: High resolution, clear annotations
- **Quantity Target**: 100+ drawings

### Structural Drawings  
- **Element Types**: Beams, columns, slabs, foundations, reinforcement
- **File Formats**: PDF, DWG, DXF
- **Quality**: Clear structural elements, load calculations
- **Quantity Target**: 100+ drawings

### Civil Drawings
- **Element Types**: Site plans, grading, drainage, utilities, roads
- **File Formats**: PDF, DWG, DXF
- **Quality**: Topographic data, utility layouts
- **Quantity Target**: 50+ drawings

### MEP Drawings
- **Element Types**: HVAC, electrical, plumbing, fire protection
- **File Formats**: PDF, DWG, DXF
- **Quality**: Clear system layouts, equipment specs
- **Quantity Target**: 100+ drawings

## Annotation Standards

### Element Annotation Format
```json
{
  "drawing_id": "string",
  "discipline": "architectural|structural|civil|mep",
  "elements": [
    {
      "id": "unique_id",
      "type": "element_type",
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.95,
      "properties": {
        "dimensions": "string",
        "material": "string",
        "specifications": "string"
      }
    }
  ]
}
```

### Quality Control
- Minimum 2 annotators per drawing
- Inter-annotator agreement > 85%
- Regular validation checks
- Version control for annotations

## Data Processing Pipeline

1. **Raw Data Collection** → `raw/`
2. **Preprocessing** → `processed/`
3. **Annotation** → `annotations/`
4. **Metadata Extraction** → `metadata/`
5. **Dataset Creation** → `datasets/`

## Usage

See individual discipline directories for specific guidelines and examples. 