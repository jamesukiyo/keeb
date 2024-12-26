import os
from collections import Counter
from pathlib import Path
import argparse
import csv

def should_skip_file(filepath):
   """Determine if file should be skipped based on extension or path"""
   skip_extensions = {
       '.pyc', '.exe', '.dll', '.so', '.dylib', '.json',
       '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', 
       '.pdf', '.zip', '.tar', '.gz', '.7z', '.webp',
       '.mp3', '.mp4', '.avi', '.mov', '.yaml', '.jar',
       '.ttf', '.woff', '.woff2', '.cursorrules', '.ipynb',
       '.pkl', '.h5', '.model', '.txt', '.class', '.tree'
   }
   
   skip_dirs = {
       'node_modules', 'venv', 'env', '.git', '.svelte-kit', '.mvn',
       '__pycache__', 'build', 'dist', '.idea', '.husky', '.turbo'
   }
   
   path = Path(filepath)
   if path.suffix.lower() in skip_extensions:
       return True
   if any(part in skip_dirs for part in path.parts): 
       return True
   return False

def scan_repo(repo_path):
   """Scan repository and count character occurrences"""
   char_count = Counter()
   file_count = 0
   error_files = []

   for root, _, files in os.walk(repo_path):
       for file in files:
           filepath = os.path.join(root, file)
           
           if should_skip_file(filepath):
               continue
               
           try:
               with open(filepath, 'r', encoding='utf-8') as f:
                   content = f.read()
                   char_count.update(content)
                   file_count += 1
           except (UnicodeDecodeError, PermissionError, FileNotFoundError) as e:
               error_files.append((filepath, str(e)))
               continue

   return char_count, file_count, error_files

def print_results(char_count, file_count, error_files, top_n=50, show_spaces=False, save_csv=False, exclude_letters=False):
   """Print analysis results and optionally save as CSV"""
   print(f"\nProcessed {file_count} files")
   
   total_chars = sum(char_count.values())
   print(f"Total characters: {total_chars:,}")
   
   print("\nTop character frequencies:")
   print("Char | Count | Percentage")
   print("-" * 30)

   results = []
   for char, count in char_count.most_common():
       if exclude_letters and char.isalpha():
           continue
       if char.isspace() and not show_spaces:
           continue
       if char.isspace():
           char_display = f"'{char}'" if char == ' ' else f'\\{char}'
       else:
           char_display = char
       percentage = (count / total_chars) * 100
       print(f"{char_display:4} | {count:7,} | {percentage:6.2f}%")
       results.append((char_display, count, percentage))
       if len(results) >= top_n:
           break

   if save_csv:
       csv_path = Path.cwd() / "char_freqs.csv"
       with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
           writer = csv.writer(csv_file)
           writer.writerow(["Character", "Count", "Percentage"])
           writer.writerows(results)
       print(f"\nResults saved to {csv_path}")

   if error_files:
       print("\nFiles with errors:")
       for filepath, error in error_files:
           print(f"- {filepath}: {error}")

def main():
   parser = argparse.ArgumentParser(description='Analyse character frequencies in a repository')
   parser.add_argument('repo_path', help='Path to the repository')
   parser.add_argument('--top', type=int, default=50, help='Number of top characters to display')
   parser.add_argument('--show-spaces', action='store_true', help='Include spaces and whitespace characters in the output')
   parser.add_argument('--save-csv', action='store_true', help='Save results as CSV in the current working directory')
   parser.add_argument('--exclude-letters', action='store_true', help='Exclude all letters (A-Z, a-z) from the output')
   args = parser.parse_args()

   print(f"Scanning repository: {args.repo_path}")
   char_count, file_count, error_files = scan_repo(args.repo_path)
   print_results(char_count, file_count, error_files, args.top, args.show_spaces, args.save_csv, args.exclude_letters)

if __name__ == '__main__':
   main()