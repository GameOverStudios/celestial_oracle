import sqlite3
from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('teste.html')

@app.route('/categorias_json')
def categorias_json():
    conn = sqlite3.connect('categorias.db')
    cursor = conn.cursor()

    categorias = {}
    for row in cursor.execute('SELECT id, name, parent_id FROM Categorias'):
        categoria_id, name, parent_id = row
        categorias[categoria_id] = {'name': name, 'parent_id': parent_id, 'children': []}

    for row in cursor.execute('SELECT id, name, categoria_id FROM Itens'):
        item_id, name, categoria_id = row
        categorias[categoria_id]['children'].append({'name': name, 'value': item_id})

    def build_hierarchy(categoria_id):
        categoria = categorias[categoria_id]
        children = []
        for child_id, child in categorias.items():
            if child['parent_id'] == categoria_id:
                children.append(build_hierarchy(child_id))

        return {
            'name': categoria['name'],
            'children': children + categoria['children']
        }

    raiz = [build_hierarchy(categoria_id) for categoria_id, categoria in categorias.items() if not categoria['parent_id']]

    conn.close()
    return jsonify(raiz[0] if len(raiz) == 1 else raiz)

if __name__ == "__main__":
    app.run(debug=True)
