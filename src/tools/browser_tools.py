"""Native tools for browser operations"""
import os
import webbrowser
from pathlib import Path


class BrowserTools:
    """Tools for saving and opening HTML in browser"""
    
    def save_and_open_html(self, html_content: str, impairment_name: str) -> dict:
        """
        Save HTML content to a file and open it in the default browser.
        
        Args:
            html_content: The HTML content to save
            impairment_name: Name of the impairment (used in filename)
            
        Returns:
            Dict with file_path, success status, and message
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            # Create filename from impairment name
            safe_name = impairment_name.replace(" ", "_").replace("/", "_")
            filename = f"decision_tree_{safe_name}.html"
            file_path = output_dir / filename
            
            # Save HTML content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Open in browser
            webbrowser.open(f"file://{file_path.absolute()}")
            
            return {
                "html_file_path": str(file_path),
                "success": True,
                "message": f"HTML saved to {file_path} and opened in browser"
            }
            
        except Exception as e:
            return {
                "html_file_path": "",
                "success": False,
                "message": f"Error: {str(e)}"
            }
