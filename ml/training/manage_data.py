#!/usr/bin/env python3
"""
Training Data Management CLI Tool

This script provides a command-line interface for managing training data
collection, preprocessing, and validation for the Construction AI system.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Add the training directory to the path
sys.path.append(str(Path(__file__).parent))

from data_collector import TrainingDataCollector, AnnotationManager
from data_preprocessor import DataPreprocessor, DataValidator

def collect_drawing(args):
    """Collect a drawing file into the training data structure."""
    collector = TrainingDataCollector(args.base_path)
    
    try:
        # Parse metadata if provided
        metadata = None
        if args.metadata:
            metadata = json.loads(args.metadata)
        
        drawing_id = collector.collect_drawing(
            file_path=args.file_path,
            discipline=args.discipline,
            metadata=metadata
        )
        
        print(f"✅ Successfully collected drawing: {drawing_id}")
        return drawing_id
        
    except Exception as e:
        print(f"❌ Error collecting drawing: {e}")
        return None

def create_annotation(args):
    """Create an annotation file for a drawing."""
    annotation_mgr = AnnotationManager(args.base_path)
    
    try:
        # Load elements from file or use sample data
        if args.elements_file:
            with open(args.elements_file, 'r') as f:
                elements = json.load(f)
        else:
            # Create sample annotation
            elements = [
                {
                    "id": "sample_element_001",
                    "type": "wall",
                    "bbox": [100, 100, 200, 150],
                    "confidence": 0.95,
                    "properties": {
                        "thickness": "200mm",
                        "material": "concrete"
                    }
                }
            ]
        
        annotation_path = annotation_mgr.create_annotation(
            drawing_id=args.drawing_id,
            discipline=args.discipline,
            elements=elements
        )
        
        print(f"✅ Created annotation: {annotation_path}")
        return annotation_path
        
    except Exception as e:
        print(f"❌ Error creating annotation: {e}")
        return None

def preprocess_drawing(args):
    """Preprocess a drawing for training."""
    preprocessor = DataPreprocessor(args.base_path)
    
    try:
        target_size = tuple(map(int, args.target_size.split('x'))) if args.target_size else None
        
        processed_path = preprocessor.preprocess_drawing(
            drawing_id=args.drawing_id,
            discipline=args.discipline,
            target_size=target_size
        )
        
        print(f"✅ Preprocessed drawing: {processed_path}")
        return processed_path
        
    except Exception as e:
        print(f"❌ Error preprocessing drawing: {e}")
        return None

def create_dataset(args):
    """Create a training dataset for a discipline."""
    preprocessor = DataPreprocessor(args.base_path)
    
    try:
        dataset_config = preprocessor.create_training_dataset(
            discipline=args.discipline,
            split_ratio=args.split_ratio
        )
        
        print(f"✅ Created dataset for {args.discipline}:")
        print(f"   Total drawings: {dataset_config['total_drawings']}")
        print(f"   Training: {dataset_config['train_drawings']}")
        print(f"   Validation: {dataset_config['val_drawings']}")
        
        return dataset_config
        
    except Exception as e:
        print(f"❌ Error creating dataset: {e}")
        return None

def validate_dataset(args):
    """Validate a dataset for a discipline."""
    validator = DataValidator(args.base_path)
    
    try:
        validation_results = validator.validate_dataset(args.discipline)
        
        print(f"📊 Validation Results for {args.discipline}:")
        print(f"   Status: {validation_results['status']}")
        print(f"   Raw files: {validation_results['statistics']['raw_files']}")
        print(f"   Processed files: {validation_results['statistics']['processed_files']}")
        print(f"   Annotations: {validation_results['statistics']['annotations']}")
        
        if validation_results['errors']:
            print("   ❌ Errors:")
            for error in validation_results['errors']:
                print(f"      - {error}")
        
        if validation_results['warnings']:
            print("   ⚠️  Warnings:")
            for warning in validation_results['warnings']:
                print(f"      - {warning}")
        
        return validation_results
        
    except Exception as e:
        print(f"❌ Error validating dataset: {e}")
        return None

def show_statistics(args):
    """Show statistics for all training data."""
    collector = TrainingDataCollector(args.base_path)
    
    try:
        stats = collector.get_statistics()
        
        print("📈 Training Data Statistics:")
        print("=" * 50)
        
        total_drawings = 0
        total_size = 0
        
        for discipline, discipline_stats in stats.items():
            print(f"\n🏗️  {discipline.upper()}:")
            print(f"   Drawings: {discipline_stats['total_drawings']}")
            print(f"   Size: {discipline_stats['total_size_mb']} MB")
            
            if discipline_stats['file_formats']:
                print("   Formats:")
                for fmt, count in discipline_stats['file_formats'].items():
                    print(f"     {fmt}: {count}")
            
            total_drawings += discipline_stats['total_drawings']
            total_size += discipline_stats['total_size_mb']
        
        print(f"\n📊 TOTAL:")
        print(f"   Drawings: {total_drawings}")
        print(f"   Size: {total_size} MB")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return None

def list_drawings(args):
    """List all drawings for a discipline."""
    collector = TrainingDataCollector(args.base_path)
    
    try:
        drawings = collector.get_drawings_by_discipline(args.discipline)
        
        print(f"📋 Drawings for {args.discipline}:")
        print("=" * 40)
        
        if not drawings:
            print("   No drawings found.")
        else:
            for i, drawing_id in enumerate(drawings, 1):
                print(f"   {i:3d}. {drawing_id}")
        
        return drawings
        
    except Exception as e:
        print(f"❌ Error listing drawings: {e}")
        return None

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Training Data Management Tool for Construction AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect a drawing
  python manage_data.py collect --file-path drawing.pdf --discipline architectural
  
  # Create annotation
  python manage_data.py annotate --drawing-id arch_abc123 --discipline architectural
  
  # Preprocess drawing
  python manage_data.py preprocess --drawing-id arch_abc123 --discipline architectural
  
  # Create dataset
  python manage_data.py dataset --discipline architectural
  
  # Validate dataset
  python manage_data.py validate --discipline architectural
  
  # Show statistics
  python manage_data.py stats
  
  # List drawings
  python manage_data.py list --discipline architectural
        """
    )
    
    parser.add_argument(
        '--base-path',
        default='ml/data',
        help='Base path for training data (default: ml/data)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect a drawing file')
    collect_parser.add_argument('--file-path', required=True, help='Path to drawing file')
    collect_parser.add_argument('--discipline', required=True, 
                               choices=['architectural', 'structural', 'civil', 'mep'],
                               help='Discipline category')
    collect_parser.add_argument('--metadata', help='JSON metadata string')
    collect_parser.set_defaults(func=collect_drawing)
    
    # Annotate command
    annotate_parser = subparsers.add_parser('annotate', help='Create annotation for drawing')
    annotate_parser.add_argument('--drawing-id', required=True, help='Drawing ID')
    annotate_parser.add_argument('--discipline', required=True,
                                choices=['architectural', 'structural', 'civil', 'mep'],
                                help='Discipline category')
    annotate_parser.add_argument('--elements-file', help='JSON file with elements data')
    annotate_parser.set_defaults(func=create_annotation)
    
    # Preprocess command
    preprocess_parser = subparsers.add_parser('preprocess', help='Preprocess a drawing')
    preprocess_parser.add_argument('--drawing-id', required=True, help='Drawing ID')
    preprocess_parser.add_argument('--discipline', required=True,
                                  choices=['architectural', 'structural', 'civil', 'mep'],
                                  help='Discipline category')
    preprocess_parser.add_argument('--target-size', help='Target size (e.g., 1024x1024)')
    preprocess_parser.set_defaults(func=preprocess_drawing)
    
    # Dataset command
    dataset_parser = subparsers.add_parser('dataset', help='Create training dataset')
    dataset_parser.add_argument('--discipline', required=True,
                               choices=['architectural', 'structural', 'civil', 'mep'],
                               help='Discipline category')
    dataset_parser.add_argument('--split-ratio', type=float, default=0.8,
                               help='Train/validation split ratio (default: 0.8)')
    dataset_parser.set_defaults(func=create_dataset)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate dataset')
    validate_parser.add_argument('--discipline', required=True,
                                choices=['architectural', 'structural', 'civil', 'mep'],
                                help='Discipline category')
    validate_parser.set_defaults(func=validate_dataset)
    
    # Statistics command
    stats_parser = subparsers.add_parser('stats', help='Show training data statistics')
    stats_parser.set_defaults(func=show_statistics)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List drawings for discipline')
    list_parser.add_argument('--discipline', required=True,
                            choices=['architectural', 'structural', 'civil', 'mep'],
                            help='Discipline category')
    list_parser.set_defaults(func=list_drawings)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute the command
    args.func(args)

if __name__ == "__main__":
    main() 