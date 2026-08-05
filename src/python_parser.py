import ast
from pathlib import Path

import yaml

# Define paths
SOURCE_DIR = Path("src/domain/abilities/adventure/legacy_abilities")  # Path to your 123 .py files
OUTPUT_DIR = Path("src/domain/abilities/adventure")    # Path where YAML files will be generated

def parse_python_file(file_path: Path) -> dict:
    """Parses a .py file using AST to extract class attributes and variables."""
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    ability_data = {}
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"❌ Syntax error parsing {file_path.name}: {e}")
        return {}

    # Walk through the AST to find assignments (variables or class attributes)
    for node in ast.walk(tree):
        # Handle standard variable assignments (e.g., NAME = "Fireball")
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    key = target.id.lower()
                    try:
                        ability_data[key] = ast.literal_eval(node.value)
                    except ValueError:
                        # Fallback for complex expressions or logic we can't literal_eval
                        ability_data[key] = ast.unparse(node.value)
                        
        # Handle class definitions and their internal attributes
        elif isinstance(node, ast.ClassDef):
            for body_item in node.body:
                if isinstance(body_item, ast.Assign):
                    for target in body_item.targets:
                        if isinstance(target, ast.Name):
                            key = target.id.lower()
                            try:
                                ability_data[key] = ast.literal_eval(body_item.value)
                            except ValueError:
                                ability_data[key] = ast.unparse(body_item.value)
                                
                # Optional: Capture existing function signatures/bodies as text strings
                elif isinstance(body_item, ast.FunctionDef):
                    func_name = body_item.name
                    if func_name not in ["__init__"]:
                        # Convert code logic straight into a formula/string string
                        ability_data[f"formula_{func_name}"] = ast.unparse(body_item.body).strip()

    return ability_data

def determine_target_folder(file_path: Path, data: dict) -> Path:
    """Determines the appropriate output folder matching your file taxonomy."""
    # 1. Preserve original structure if legacy files are already split by folders
    # (e.g., combat, generic, utility, or job specific)
    relative_path = file_path.relative_to(SOURCE_DIR).parent
    if relative_path != Path("."):
        return OUTPUT_DIR / relative_path
        
    # 2. Fallback heuristic: Parse data keywords to guess taxonomy if it's currently a flat folder
    jobs = data.get("jobs_required", {}) or data.get("jobs", [])
    ability_type = str(data.get("type", "")).lower()
    
    if len(jobs) > 1 or "all" in jobs:
        if "heal" in ability_type or "buff" in ability_type:
            return OUTPUT_DIR / "shared" / "utility"
        return OUTPUT_DIR / "shared" / "combat"
        
    if len(jobs) == 1:
        single_job = list(jobs)[0] if isinstance(jobs, dict) else jobs[0]
        return OUTPUT_DIR / single_job
        
    return OUTPUT_DIR / "shared" / "generic"

def clean_and_format_data(data: dict) -> dict:
    """Normalizes job requirements and strips out unneeded legacy code blocks."""
    cleaned = {}
    
    # Map old keys to new standardized schema keys
    key_mapping = {
        "name": "name",
        "type": "type",
        "cooldown": "cooldown",
        "mana_cost": "mana_cost",
        "mp_cost": "mana_cost"
    }
    
    for old_key, new_key in key_mapping.items():
        if old_key in data:
            cleaned[new_key] = data[old_key]
            
    # Handle the evolution of Job mapping to Level Requirements
    # If legacy data already has jobs_required dictionary, use it
    if "jobs_required" in data and isinstance(data["jobs_required"], dict):
        cleaned["jobs_required"] = data["jobs_required"]
    # If legacy data just has a plain old 'jobs' list, default everyone to Level 1
    elif "jobs" in data and isinstance(data["jobs"], list):
        cleaned["jobs_required"] = {job: 1 for job in data["jobs"]}
    else:
        cleaned["jobs_required"] = {"all": 1}
        
    # Carry over remaining attributes (damage, effects, etc.)
    for k, v in data.items():
        if k not in key_mapping and k not in ["jobs", "jobs_required"]:
            cleaned[k] = v
            
    return cleaned

def run_migration():
    print("🚀 Starting bulk ability migration...")
    success_count = 0
    
    # Find all .py files recursively in source directory
    py_files = list(SOURCE_DIR.rglob("*.py"))
    
    for file_path in py_files:
        if file_path.name == "__init__.py":
            continue
            
        # 1. Parse raw data out of python file
        raw_data = parse_python_file(file_path)
        if not raw_data:
            continue
            
        # 2. Standardize data structure to matches our clean new schema
        clean_data = clean_and_format_data(raw_data)
        
        # 3. Figure out target subdirectory route
        target_folder = determine_target_folder(file_path, clean_data)
        target_folder.mkdir(parents=True, exist_ok=True)
        
        # 4. Write YAML file
        yaml_filename = f"{file_path.stem}.yaml"
        target_file = target_folder / yaml_filename
        
        with open(target_file, "w", encoding="utf-8") as yf:
            yaml.dump(clean_data, yf, sort_keys=False, allow_unicode=True, default_flow_style=False)
            
        print(f"✅ Migrated: {file_path.name} -> {target_file.relative_to(OUTPUT_DIR.parent)}")
        success_count += 1

    print(f"\n🎉 Migration Complete! Successfully converted {success_count} files.")

if __name__ == "__main__":
    run_migration()
