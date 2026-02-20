# -*- coding: utf-8 -*-
import json

class FlowNode:
    def __init__(self, id, type, label, children=None):
        self.id = id
        self.type = type # 'start', 'end', 'process', 'decision', 'loop', 'call'
        self.label = label
        self.next = [] # List of IDs it points to
        self.children = children or [] # For nested blocks (if/while)

class FlowchartGenerator:
    def __init__(self):
        self.node_count = 0
        self.nodes = []

    def _next_id(self):
        self.node_count += 1
        return f"node_{self.node_count}"

    def generate(self, ast):
        self.nodes = []
        self.node_count = 0
        
        start_node = FlowNode(self._next_id(), "start", "BAŞLA")
        self.nodes.append(start_node)
        
        last_node_id = self._process_statements(ast.statements, start_node.id)
        
        end_node = FlowNode(self._next_id(), "end", "BİTİR")
        self.nodes.append(end_node)
        
        if last_node_id:
            self._get_node(last_node_id).next.append(end_node.id)
        else:
            start_node.next.append(end_node.id)
            
        return self.nodes

    def _get_node(self, id):
        for n in self.nodes:
            if n.id == id: return n
        return None

    def _process_statements(self, statements, last_id):
        current_id = last_id
        for stmt in statements:
            if not stmt: continue
            
            stmt_json = stmt.to_json()
            type = stmt_json.get("type")
            
            if type == "VarStmt":
                new_id = self._next_id()
                label = f"Tanımla: {stmt_json['value']}"
                node = FlowNode(new_id, "process", label)
                self.nodes.append(node)
                self._get_node(current_id).next.append(new_id)
                current_id = new_id
                
            elif type == "PrintStmt":
                new_id = self._next_id()
                node = FlowNode(new_id, "process", "Yazdır")
                self.nodes.append(node)
                self._get_node(current_id).next.append(new_id)
                current_id = new_id
                
            elif type == "IfStmt":
                decision_id = self._next_id()
                node = FlowNode(decision_id, "decision", "Eğer?")
                self.nodes.append(node)
                self._get_node(current_id).next.append(decision_id)
                
                # Logic for If: Draw then branch
                # For a simple vertical flowchart, we just process then branch then join back
                # This is a simplification but better than nothing
                if hasattr(stmt, 'then_branch'):
                    # If it's a BlockStmt, process its statements
                    if hasattr(stmt.then_branch, 'statements'):
                        branch_last = self._process_statements(stmt.then_branch.statements, decision_id)
                    else:
                        branch_last = self._process_statements([stmt.then_branch], decision_id)
                    
                    current_id = branch_last
                else:
                    current_id = decision_id
                
            elif type == "WhileStmt":
                loop_id = self._next_id()
                node = FlowNode(loop_id, "loop", "Döngü")
                self.nodes.append(node)
                self._get_node(current_id).next.append(loop_id)
                
                if hasattr(stmt, 'body'):
                    if hasattr(stmt.body, 'statements'):
                        self._process_statements(stmt.body.statements, loop_id)
                    else:
                        self._process_statements([stmt.body], loop_id)
                
                current_id = loop_id
                
            elif type == "FunctionStmt":
                new_id = self._next_id()
                node = FlowNode(new_id, "call", f"Fonksiyon: {stmt_json['value']}")
                self.nodes.append(node)
                self._get_node(current_id).next.append(new_id)
                current_id = new_id
                
            elif type == "ExprStmt":
                # Check if it's a CallExpr
                label = "İşlem"
                inner = stmt_json.get("children", [{}])[0]
                if inner.get("type") == "CallExpr":
                    label = "Çağır"
                
                new_id = self._next_id()
                node = FlowNode(new_id, "process", label)
                self.nodes.append(node)
                self._get_node(current_id).next.append(new_id)
                current_id = new_id
                
        return current_id
