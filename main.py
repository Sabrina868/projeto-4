import flet as ft
import requests
from connect import get_livros
from urllib.parse import urlparse, parse_qs

def main(page: ft.Page):
    page.title = "Cadastro App"
    page.window.width = 400

    def home_page():
        nome_input = ft.TextField(label="Nome do produto", text_align=ft.TextAlign.LEFT)

        streaming_select = ft.Dropdown(
            options=[
                ft.dropdown.Option("AK", text='Amazon Kindle'),
                ft.dropdown.Option("F", text='Físico'),
            ],
            label='Selecione a streaming'
        )

        def carregar_livros():
            lista_livros.controls.clear()
            for livro in get_livros():
                lista_livros.controls.append(
                    ft.Container(
                        ft.Text(livro['nome']),
                        bgcolor=ft.colors.BLACK12,
                        padding=15,
                        alignment=ft.alignment.center,
                        margin=3,
                        border_radius=10,
                        on_click=lambda e, livro_id=livro["id"]: page.go(f'/review?id={livro_id}')  # Passa o ID do livro na URL
                    )
                )
            page.update()

        def cadastrar(e):
            data = {
                'nome': nome_input.value,
                'streaming': streaming_select.value,
                'categorias': [],  # Desenvolver a lógica para categorias
            }
            requests.post('http://127.0.0.1:8000/api/livros/', json=data)
            carregar_livros()

        cadastrar_btn = ft.ElevatedButton(text="Cadastrar", on_click=cadastrar)

        lista_livros = ft.ListView()
        lista_livros.controls.append(
            ft.Container(
                ft.Text('livro 1')
            )
        )

        carregar_livros()
        page.views.append(
            ft.View(
                "/",
                controls=[
                    nome_input,
                    streaming_select,
                    cadastrar_btn,
                    lista_livros
                ]
            )
        )

    def review_page(livro_id):
        nota_input = ft.TextField(label="Nota (inteiro)", text_align=ft.TextAlign.LEFT, value='0', width=100)
        comentario_input = ft.TextField(label="Comentário", multiline=True, expand=True)

        def avaliar(e):
            data = {
                'nota': int(nota_input.value),
                'comentario': comentario_input.value
            }

            try:
                response = requests.post(f'http://127.0.0.1:8000/api/livros/{livro_id}', json=data)

                if response.status_code in [200, 201]:
                    page.overlay.append(ft.SnackBar(ft.Text("Avaliação feita com sucesso!")))
                else:
                    error_message = response.json().get("detail", "Erro ao enviar avaliação")
                    page.overlay.append(ft.SnackBar(ft.Text(f"Erro: {error_message}")))
                page.overlay[-1].open = True
            except requests.exceptions.RequestException as e:
                page.overlay.append(ft.SnackBar(ft.Text(f'Erro de Conexão: {e}')))
                page.overlay[-1].open = True

            page.update()

        avaliar_btn = ft.ElevatedButton(text="Avaliar", on_click=avaliar)
        voltar_btn = ft.ElevatedButton(text="Voltar", on_click=lambda _: page.go("/"))

        page.views.append(
            ft.View(
                "/review",
                controls=[
                    ft.Text(f"Livro ID: {livro_id}"),
                    nota_input,
                    comentario_input,
                    avaliar_btn,
                    voltar_btn
                ]
            )
        )

    def route_change(e):
        page.views.clear()
        if page.route == "/":
            home_page()
        elif page.route.startswith('/review'):
            parsed_url = urlparse(page.route)
            query_params = parse_qs(parsed_url.query)
            if 'id' in query_params:
                livro_id = query_params['id'][0]
                review_page(livro_id)
            else:
                print("ID do livro não encontrado na URL")
        page.update()

    page.on_route_change = route_change
    page.go("/")  # Define a rota inicial para "/"

ft.app(target=main)
