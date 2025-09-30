from app import app, db, Produto, caminho_local_por_sku


def add_produto(sku: str, marca: str, modelo: str, cor: str, tamanho: str, preco: float) -> None:
    local_path = caminho_local_por_sku(sku, modelo)
    produto = Produto(
        sku=sku,
        marca=marca,
        modelo=modelo,
        cor=cor,
        tamanho=tamanho,
        preco=preco,
        imagem_url=local_path,
        descricao=modelo,
    )
    db.session.add(produto)


def main() -> None:
    with app.app_context():
        # Limpa estoque atual
        for p in Produto.query.all():
            db.session.delete(p)
        db.session.commit()

        # Recria com os dois modelos solicitados
        add_produto(
            "CZ0790-106",
            "Jordan",
            "Air Jordan 1 Low OG Chicago",
            "Vermelho",
            "42",
            1599.90,
        )
        add_produto(
            "DM7866-140",
            "Jordan",
            "Fragment x Travis Scott x Air Jordan 1 Low OG SP Sail Military Blue",
            "Azul",
            "42",
            2199.90,
        )
        db.session.commit()
        print("Estoque atualizado para 2 itens.")


if __name__ == "__main__":
    main()


