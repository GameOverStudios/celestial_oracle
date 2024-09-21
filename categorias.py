import sqlite3
import argparse

def create_tables(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        parent_id INTEGER,
        FOREIGN KEY (parent_id) REFERENCES Categorias(id)
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        categoria_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES Categorias(id)
    );
    ''')

def insert_categoria(cursor, name, parent_id=None):
    cursor.execute('INSERT OR IGNORE INTO Categorias (name, parent_id) VALUES (?, ?);', (name, parent_id))

def insert_item(cursor, name, categoria_id):
    cursor.execute('INSERT INTO Itens (name, categoria_id) VALUES (?, ?);', (name, categoria_id))

def categoria_exists(cursor, name):
    return cursor.execute('SELECT id FROM Categorias WHERE name = ?;', (name,)).fetchone()

def relate_categoria(cursor, categoria_name, parent_name):
    categoria_id = categoria_exists(cursor, categoria_name)
    parent_id = categoria_exists(cursor, parent_name)
    
    if categoria_id and parent_id:
        if categoria_id[0] != parent_id[0]:  # Evita ciclo
            cursor.execute('UPDATE Categorias SET parent_id = ? WHERE id = ?;', (parent_id[0], categoria_id[0]))
            print(f'Categoria "{categoria_name}" relacionada a "{parent_name}".')
        else:
            print(f'Erro: não é possível relacionar uma categoria a si mesma.')
    else:
        print(f'Erro ao relacionar "{categoria_name}" com "{parent_name}".')

def list_categorias(cursor, parent_id=None, indent=0):
    query = 'SELECT id, name FROM Categorias WHERE parent_id IS ? ORDER BY name;'
    cursor.execute(query, (parent_id,))
    rows = cursor.fetchall()
    for row in rows:
        print('  ' * indent + f'- {row[1]} (ID: {row[0]})')
        list_itens(cursor, row[0], indent)
        list_categorias(cursor, row[0], indent + 1)



def list_itens(cursor, categoria_id, indent):
    cursor.execute('SELECT name FROM Itens WHERE categoria_id = ?;', (categoria_id,))
    items = cursor.fetchall()
    if items:
        print('  ' * (indent + 1) + "Itens:")
        for item in items:
            print('  ' * (indent + 2) + f"- {item[0]}")

def main():
    parser = argparse.ArgumentParser(description='Gerenciar categorias e itens no banco de dados.')
    parser.add_argument('--add_categoria', type=str, help='Nome da nova categoria a ser criada.')
    parser.add_argument('--add_item', type=str, help='Nome do item a ser adicionado.')
    parser.add_argument('--categoria', type=str, help='Nome da categoria para o item.')
    parser.add_argument('--relate_categoria', nargs=2, help='Relacione uma categoria a um pai (categoria, pai).')
    parser.add_argument('--list_categorias', action='store_true', help='Listar todas as categorias e itens.')

    args = parser.parse_args()

    conn = sqlite3.connect('categorias.db')
    cursor = conn.cursor()

    create_tables(cursor)

    if args.add_categoria:
        insert_categoria(cursor, args.add_categoria)
        print(f'Categoria "{args.add_categoria}" cadastrada.')
        list_categorias(cursor, parent_id=None)  # Assegure-se de passar None

    if args.add_item and args.categoria:
        categoria_id = categoria_exists(cursor, args.categoria)
        if categoria_id:
            insert_item(cursor, args.add_item, categoria_id[0])
            print(f'Item "{args.add_item}" adicionado à categoria "{args.categoria}".')
        else:
            print(f'Categoria "{args.categoria}" não encontrada.')

    if args.relate_categoria:
        relate_categoria(cursor, args.relate_categoria[0], args.relate_categoria[1])

    if args.list_categorias:
        print("\nCategorias cadastradas:")
        list_categorias(cursor)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()


'''

python categorias.py --add_categoria "72 Cartas"

python categorias.py --add_categoria "22 Arcanos Maiores"
python categorias.py --add_categoria "56 Arcanos Menores"

python categorias.py --relate_categoria "22 Arcanos Maiores" "72 Cartas"
python categorias.py --relate_categoria "56 Arcanos Menores" "72 Cartas"

python categorias.py --add_categoria "Copas"
python categorias.py --relate_categoria "Copas" "56 Arcanos Menores"

python categorias.py --add_item "0 O Louco" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "1 O Mago" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "2 A Sacerdotisa" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "3 A Imperatriz" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "4 O Imperador" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "5 O Hierofante" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "6 Os Amantes" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "7 O Carro" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "8 A Força" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "9 O Eremita" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "10 A Roda da Fortuna" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "11 A Justiça" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "12 O Enforcado" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "13 A Morte" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "14 A Temperança" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "15 O Diabo" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "16 A Torre" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "17 A Estrela" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "18 A Lua" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "19 O Sol" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "20 O Julgamento" --categoria "22 Arcanos Maiores"
python categorias.py --add_item "21 O Mundo" --categoria "22 Arcanos Maiores"

python categorias.py --add_item "As de Copas" --categoria "Copas"
python categorias.py --add_item "Dois de Copas" --categoria "Copas"
python categorias.py --add_item "Três de Copas" --categoria "Copas"
python categorias.py --add_item "Quatro de Copas" --categoria "Copas"
python categorias.py --add_item "Cinco de Copas" --categoria "Copas"
python categorias.py --add_item "Seis de Copas" --categoria "Copas"
python categorias.py --add_item "Sete de Copas" --categoria "Copas"
python categorias.py --add_item "Oito de Copas" --categoria "Copas"
python categorias.py --add_item "Nove de Copas" --categoria "Copas"
python categorias.py --add_item "Dez de Copas" --categoria "Copas"
python categorias.py --add_item "Valete de Copas" --categoria "Copas"
python categorias.py --add_item "Cavaleiro de Copas" --categoria "Copas"
python categorias.py --add_item "Rainha de Copas" --categoria "Copas"
python categorias.py --add_item "Rei de Copas" --categoria "Copas"

python categorias.py --list_categorias

Categorias cadastradas:
- 72 Cartas (ID: 1)
  - 22 Arcanos Maiores (ID: 2)
    Itens:
      - 0 O Louco
      - 1 O Mago
  - 56 Arcanos Menores (ID: 3)
    - Copas (ID: 4)
      Itens:
        - As de Copas
        - Dois de Copas

'''