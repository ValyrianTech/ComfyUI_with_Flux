#!/usr/bin/env python3
"""
CivitAI URL Preprocessor - Standalone Script
Converts non-download URLs to proper download URLs using CivitAI API
"""

import asyncio
import sys
import argparse
from pathlib import Path

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="CivitAI URL Preprocessor - Convert non-download URLs to proper download URLs"
    )
    
    parser.add_argument(
        "--api-key",
        dest="api_key",
        type=str,
        help="CivitAI API key for authentication (recommended for better results)"
    )
    
    parser.add_argument(
        "--csv-dir",
        dest="csv_dir",
        type=str,
        default="CSVs",
        help="Directory containing CSV files to process (default: CSVs)"
    )
    
    parser.add_argument(
        "--file",
        dest="single_file",
        type=str,
        help="Process a single CSV or text file instead of directory"
    )
    
    parser.add_argument(
        "--url",
        dest="single_url",
        type=str,
        help="Process a single URL/ID/name and display the result"
    )
    
    parser.add_argument(
        "--text-files",
        action="store_true",
        help="Include .txt files when processing directories (creates CSV output)"
    )
    
    return parser.parse_args()

async def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Setup logging
    from loguru import logger
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True
    )
    
    # Import preprocessing functionality
    from .preprocess import URLPreprocessor, preprocess_urls, process_single_url
    
    print("🔄 CivitAI URL Preprocessor")
    print("=" * 40)
    
    if not args.api_key:
        print("⚠️  Warning: No API key provided. Some protected models may not be accessible.")
        print("For better results, use: python preprocess.py --api-key YOUR_API_KEY")
        print()
    
    if args.single_url:
        # Process single URL
        print(f"🔗 Processing single URL: {args.single_url}")
        success, result, metadata = await process_single_url(args.single_url, args.api_key)
        
        if success:
            print(f"\n✅ Successfully resolved!")
            print(f"📥 Download URL: {result}")
            if metadata:
                print(f"📋 Metadata:")
                for key, value in metadata.items():
                    if key != 'download_url':  # Already shown above
                        print(f"   {key.replace('_', ' ').title()}: {value}")
        else:
            print(f"\n❌ Failed to resolve: {result}")
        
        return
    
    if args.single_file:
        # Process single file
        file_path = Path(args.single_file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        print(f"📁 Processing single file: {file_path.name}")
        preprocessor = URLPreprocessor(args.api_key)
        
        if file_path.suffix.lower() == '.csv':
            total, success, failed = await preprocessor.process_csv_file(file_path)
        elif file_path.suffix.lower() == '.txt':
            total, success, failed = await preprocessor.process_text_file(file_path)
        else:
            print(f"❌ Unsupported file type: {file_path.suffix}")
            print("Supported types: .csv, .txt")
            sys.exit(1)
        
        print(f"\n📊 Results for {file_path.name}:")
        print(f"  Total processed: {total}")
        print(f"  Successfully resolved: {success}")
        print(f"  Failed to resolve: {failed}")
        
        if total > 0:
            success_rate = (success / total) * 100
            print(f"  Success rate: {success_rate:.1f}%")
        
        if file_path.suffix.lower() == '.txt':
            output_csv = file_path.with_suffix('.csv')
            print(f"  CSV output: {output_csv}")
    
    else:
        # Process directory
        input_dir = Path(args.csv_dir)
        if not input_dir.exists():
            print(f"❌ Directory not found: {input_dir}")
            sys.exit(1)
        
        file_types = "CSV and text files" if args.text_files else "CSV files"
        print(f"📁 Processing {file_types} in: {input_dir}")
        results = await preprocess_urls(args.api_key, input_dir, args.text_files)
        
        if not results:
            print("No CSV files found to process")
            return
        
        # Display results
        total_all = 0
        success_all = 0
        failed_all = 0
        
        print(f"\n📊 Processing Results:")
        for filename, (total, success, failed) in results.items():
            print(f"  {filename}:")
            print(f"    Total processed: {total}")
            print(f"    Successfully resolved: {success}")
            if failed > 0:
                print(f"    Failed to resolve: {failed}")
            
            total_all += total
            success_all += success
            failed_all += failed
        
        print(f"\n📈 Overall Summary:")
        print(f"  Total URLs processed: {total_all}")
        print(f"  Successfully resolved: {success_all}")
        print(f"  Failed to resolve: {failed_all}")
        
        if total_all > 0:
            success_rate = (success_all / total_all) * 100
            print(f"  Success rate: {success_rate:.1f}%")
    
    print("\n✅ Preprocessing completed!")
    print("Your CSV files have been updated with proper download URLs.")

def run():
    """Console script entry point for the civitai-preprocess command"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Preprocessing cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
