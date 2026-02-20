# -*- coding: utf-8 -*-
import json
import webbrowser
import tempfile
import os

class AstVisualizer:
    @staticmethod
    def visualize(json_data, output_path=None):
        """JSON verisini HTML grafiğine dönüştürür"""
        
        try:
            if isinstance(json_data, str):
                ast_data = json.loads(json_data)
            else:
                ast_data = json_data
        except json.JSONDecodeError as e:
            return False, f"Geçersiz JSON verisi: {e}"

        mermaid_graph = AstVisualizer._generate_mermaid(ast_data)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Gümüşdil AST</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <style>
                body {{ background-color: #1e1e1e; color: #d4d4d4; font-family: sans-serif; margin: 0; padding: 20px; }}
                h1 {{ color: #569cd6; }}
                .container {{ background: #252526; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            </style>
        </head>
        <body>
            <h1>🌳 Gümüşdil AST Analizi</h1>
            <div class="container">
                <div class="mermaid">
{mermaid_graph}
                </div>
            </div>
            <script>
                mermaid.initialize({{
                    startOnLoad: true, 
                    theme: 'dark',
                    flowchart: {{ useMaxWidth: false, htmlLabels: true }}
                }});
            </script>
        </body>
        </html>
        """

        try:
            if not output_path:
                with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
                    output_path = f.name
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            webbrowser.open('file://' + output_path)
            return True, output_path
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _generate_mermaid(data):
        lines = ["graph TD"]
        lines.append("Program[📄 Program]")
        
        node_counter = [0]
        
        def process(node, parent_id):
            current_id = f"N{node_counter[0]}"
            node_counter[0] += 1
            
            node_type = node.get('type', 'Node')
            details = []
            
            # Önemli alanları etikete ekle
            for key in ['value', 'name', 'op', 'errorName']:
                if key in node:
                    safe_val = str(node[key]).replace('"', '').replace("'", "")
                    details.append(safe_val)
            
            label = node_type
            if details:
                label += f": {' '.join(details)}"
                
            # Node tanımı
            lines.append(f'{current_id}["{label}"]')
            # Bağlantı
            lines.append(f"{parent_id} --> {current_id}")
            
            # Recursive işleme
            for key, val in node.items():
                if isinstance(val, dict):
                    process(val, current_id)
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            process(item, current_id)
                            
        if isinstance(data, list):
            for stmt in data:
                process(stmt, "Program")
        elif isinstance(data, dict):
            process(data, "Program")
            
        return "\n".join(lines)

