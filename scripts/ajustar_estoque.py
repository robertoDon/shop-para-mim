import os
from app import app, db, Produto, caminho_local_por_sku, buscar_informacoes_produto


def main() -> None:
    valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".svg"}
    with app.app_context():
        shoes_dir = os.path.join(app.static_folder, "shoes")
        files = [f for f in os.listdir(shoes_dir) if os.path.splitext(f)[1].lower() in valid_exts]
        skus = sorted({os.path.splitext(f)[0] for f in files})

        # Limpa estoque atual
        for p in Produto.query.all():
            db.session.delete(p)
        db.session.commit()

        created = []
        for sku in skus:
            info = buscar_informacoes_produto(sku)
            marca = info.get("marca") or "Nike"
            modelo = info.get("modelo") or sku
            cor = info.get("cor") or ""
            tamanho = info.get("tamanho") or "42"
            preco = float(info.get("preco") or 0) or 999.90
            local = caminho_local_por_sku(sku, modelo) or f"/static/shoes/{sku}.webp"
            produto = Produto(
                sku=sku,
                marca=marca,
                modelo=modelo,
                cor=cor,
                tamanho=tamanho,
                preco=preco,
                imagem_url=local,
                descricao=info.get("descricao") or modelo,
            )
            db.session.add(produto)
            created.append((sku, modelo, local))

        db.session.commit()
        print(f"Estoque atualizado com {len(created)} itens:")
        for sku, modelo, local in created:
            print(f"- {sku} | {modelo} | {local}")


if __name__ == "__main__":
    main()


