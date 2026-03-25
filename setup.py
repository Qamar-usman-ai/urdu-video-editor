#!/usr/bin/env python3
"""
Setup Helper Script for Urdu Video Editor Pro
This script automates the installation process
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class SetupHelper:
    def __init__(self):
        self.system = platform.system()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.project_dir = Path(__file__).parent
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60 + "\n")
    
    def print_step(self, num, text):
        """Print step number"""
        print(f"\n📍 Step {num}: {text}")
        print("-" * 50)
    
    def check_python(self):
        """Check Python version"""
        self.print_step(1, "Checking Python Version")
        
        if sys.version_info < (3, 8):
            print(f"❌ Python {self.python_version} is too old")
            print("   Required: Python 3.8 or higher")
            return False
        
        print(f"✅ Python {self.python_version} (OK)")
        return True
    
    def check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        self.print_step(2, "Checking FFmpeg Installation")
        
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, 
                                  timeout=5)
            if result.returncode == 0:
                print("✅ FFmpeg is installed")
                return True
        except FileNotFoundError:
            pass
        
        print("❌ FFmpeg not found")
        print(f"\n   For {self.system}:")
        
        if self.system == "Windows":
            print("   1. Install Chocolatey: https://chocolatey.org/install")
            print("   2. Run: choco install ffmpeg")
        elif self.system == "Darwin":  # macOS
            print("   Install Homebrew: https://brew.sh")
            print("   Run: brew install ffmpeg")
        else:  # Linux
            print("   Run: sudo apt-get install ffmpeg")
        
        return False
    
    def create_virtual_env(self):
        """Create Python virtual environment"""
        self.print_step(3, "Creating Virtual Environment")
        
        venv_path = self.project_dir / "venv"
        
        if venv_path.exists():
            print("⚠️  Virtual environment already exists")
            return True
        
        try:
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)],
                         check=True)
            print(f"✅ Virtual environment created at {venv_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating virtual environment: {e}")
            return False
    
    def install_dependencies(self):
        """Install Python packages"""
        self.print_step(4, "Installing Python Packages")
        
        requirements_file = self.project_dir / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        # Determine pip command
        pip_cmd = [sys.executable, '-m', 'pip', 'install', 
                   '-r', str(requirements_file)]
        
        try:
            print("📦 Installing packages from requirements.txt...")
            print("   This may take a few minutes...\n")
            subprocess.run(pip_cmd, check=True)
            print("\n✅ All packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing packages: {e}")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        self.print_step(5, "Creating Project Directories")
        
        dirs_to_create = [
            Path.home() / ".urdu-video-editor" / "temp",
            Path.home() / ".urdu-video-editor" / "output",
        ]
        
        for dir_path in dirs_to_create:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created: {dir_path}")
            except Exception as e:
                print(f"❌ Error creating {dir_path}: {e}")
                return False
        
        return True
    
    def verify_installation(self):
        """Verify all components are installed"""
        self.print_step(6, "Verifying Installation")
        
        checks = {
            "app.py": self.project_dir / "app.py",
            "video_processor.py": self.project_dir / "video_processor.py",
            "voice_generator.py": self.project_dir / "voice_generator.py",
            "metadata_generator.py": self.project_dir / "metadata_generator.py",
            "config.py": self.project_dir / "config.py",
            "requirements.txt": self.project_dir / "requirements.txt",
        }
        
        all_ok = True
        for name, file_path in checks.items():
            if file_path.exists():
                print(f"✅ {name}")
            else:
                print(f"❌ {name} - NOT FOUND")
                all_ok = False
        
        # Try importing key modules
        try:
            import streamlit
            import cv2
            import numpy
            print("✅ Python packages installed")
        except ImportError as e:
            print(f"❌ Python package error: {e}")
            all_ok = False
        
        return all_ok
    
    def print_next_steps(self):
        """Print instructions for running the app"""
        self.print_header("✨ Setup Complete!")
        
        print("🎉 Your Urdu Video Editor Pro is ready!\n")
        
        print("📌 Next Steps:\n")
        print("1. Activate virtual environment:")
        
        if self.system == "Windows":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        
        print("\n2. Run the application:")
        print("   streamlit run app.py")
        
        print("\n3. Open in browser:")
        print("   http://localhost:8501")
        
        print("\n📚 Documentation:")
        print("   - Start with: QUICKSTART.md")
        print("   - Full guide: README.md")
        print("   - Issues?: TROUBLESHOOTING.md")
        
        print("\n🎬 To create your first video:")
        print("   1. Prepare 5+ video clips (MP4 format)")
        print("   2. Write your Urdu script")
        print("   3. Upload and process")
        print("   4. Download final video!")
        
        print("\n" + "="*60)
    
    def run_setup(self):
        """Run complete setup"""
        self.print_header("🎬 Urdu Video Editor Pro - Setup")
        
        steps = [
            ("Python Version", self.check_python),
            ("FFmpeg", self.check_ffmpeg),
            ("Virtual Environment", self.create_virtual_env),
            ("Python Packages", self.install_dependencies),
            ("Directories", self.create_directories),
            ("Verification", self.verify_installation),
        ]
        
        results = []
        for i, (name, func) in enumerate(steps, 1):
            try:
                result = func()
                results.append((name, result))
                if not result and name != "FFmpeg":  # FFmpeg warning only
                    print(f"\n⚠️  Setup incomplete due to {name} error")
                    return False
            except Exception as e:
                print(f"❌ Unexpected error in {name}: {e}")
                results.append((name, False))
                return False
        
        # Print summary
        print("\n" + "="*60)
        print("📊 Setup Summary:")
        print("="*60)
        for name, result in results:
            status = "✅" if result else "⚠️ "
            print(f"{status} {name}")
        
        self.print_next_steps()
        return True

def main():
    """Main entry point"""
    helper = SetupHelper()
    success = helper.run_setup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
