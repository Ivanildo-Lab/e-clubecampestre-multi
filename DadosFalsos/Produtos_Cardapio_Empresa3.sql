-- ============================================================================
-- Produtos ficticios para o CARDAPIO da empresa 3
-- Tabelas: `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` / `geficogestor$eclubecampestre_db`.`estoque_produto`
-- Como rodar (MySQL/PythonAnywhere): mysql -u <user> -p <banco> < Produtos_Cardapio_Empresa3.sql
-- Ou cole no phpMyAdmin (aba SQL). Rode 1 vez (categoria e codigo de barras sao unicos).
-- ============================================================================

-- 1) CATEGORIAS ---------------------------------------------------------------
INSERT INTO `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` (nome, descricao, data_criacao, empresa_id) VALUES
('REFRIGERANTES', 'Refrigerantes em lata e garrafa', '2026-10-13 10:00:00', 3),
('BEBIDAS', 'Cervejas, destilados e drinks', '2026-10-13 10:00:00', 3),
('COMIDAS', 'Pratos, porcoes e lanches (sem controle de estoque)', '2026-10-13 10:00:00', 3),
('BISCOITOS', 'Biscoitos e salgadinhos', '2026-10-13 10:00:00', 3),
('BOMBONS', 'Chocolates, bombons e doces', '2026-10-13 10:00:00', 3);

-- 2) REFRIGERANTES (controlam estoque) ----------------------------------------
INSERT INTO `geficogestor$eclubecampestre_db`.`estoque_produto` (nome, descricao, codigo_barras, unidade, preco_custo, preco_venda, estoque_atual, estoque_minimo, ativo, imagem, exibir_cardapio, controla_estoque, data_criacao, data_atualizacao, categoria_id, empresa_id) VALUES
('Coca-Cola Lata 350ml', 'Refrigerante Coca-Cola em lata, gelada', '7890000000011', 'UN', 3.20, 6.00, 120, 24, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'REFRIGERANTES'), 3),
('Guarana Antarctica Lata 350ml', 'Refrigerante Guarana Antarctica em lata, gelado', '7890000000028', 'UN', 3.00, 5.50, 100, 24, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'REFRIGERANTES'), 3),
('Fanta Laranja Lata 350ml', 'Refrigerante Fanta Laranja em lata, gelada', '7890000000035', 'UN', 2.90, 5.50, 80, 24, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'REFRIGERANTES'), 3),
('Coca-Cola Garrafa 2L', 'Refrigerante Coca-Cola garrafa pet 2 litros', '7890000000042', 'UN', 7.50, 12.00, 40, 12, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'REFRIGERANTES'), 3),
('Agua Mineral 500ml', 'Agua mineral sem gas, garrafa 500ml', '7890000000059', 'UN', 1.20, 3.00, 200, 48, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'REFRIGERANTES'), 3);

-- 3) BEBIDAS (controlam estoque) ----------------------------------------------
INSERT INTO `geficogestor$eclubecampestre_db`.`estoque_produto` (nome, descricao, codigo_barras, unidade, preco_custo, preco_venda, estoque_atual, estoque_minimo, ativo, imagem, exibir_cardapio, controla_estoque, data_criacao, data_atualizacao, categoria_id, empresa_id) VALUES
('Cerveja Skol Lata 350ml', 'Cerveja Skol Pilsen em lata, gelada', '7890000000066', 'UN', 2.80, 5.00, 200, 48, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BEBIDAS'), 3),
('Cerveja Heineken Long Neck 330ml', 'Cerveja Heineken garrafa long neck', '7890000000073', 'UN', 5.50, 9.00, 96, 24, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BEBIDAS'), 3),
('Caipirinha de Limao', 'Caipirinha tradicional de limao com cachaca', '7890000000080', 'UN', 4.00, 10.00, 50, 10, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BEBIDAS'), 3),
('Gin Tonica', 'Drink de gin com agua tonica e limao', '7890000000097', 'UN', 8.00, 16.00, 30, 10, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BEBIDAS'), 3),
('Dose de Whisky', 'Dose de whisky nacional', '7890000000103', 'UN', 12.00, 25.00, 20, 5, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BEBIDAS'), 3);

-- 4) COMIDAS (NAO controlam estoque: pratos e lanches) ------------------------
INSERT INTO `geficogestor$eclubecampestre_db`.`estoque_produto` (nome, descricao, codigo_barras, unidade, preco_custo, preco_venda, estoque_atual, estoque_minimo, ativo, imagem, exibir_cardapio, controla_estoque, data_criacao, data_atualizacao, categoria_id, empresa_id) VALUES
('Muqueca de Peixe', 'Muqueca de peixe com feijao, farofa e muidos. Serve 2 pessoas.', '7890000000110', 'UN', 38.00, 89.90, 0, 0, 1, '', 1, 0, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'COMIDAS'), 3),
('Feijoada Completa', 'Feijoada com arroz, couve, farofa, torresmo e laranja. Serve 2 pessoas.', '7890000000127', 'UN', 28.00, 59.90, 0, 0, 1, '', 1, 0, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'COMIDAS'), 3),
('Porcao de Batata Frita', 'Porcao de batata frita crocante com molho da casa', '7890000000134', 'UN', 12.00, 29.90, 0, 0, 1, '', 1, 0, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'COMIDAS'), 3),
('X-Burger da Casa', 'Hamburguer artesanal, queijo, alface, tomate e maionese da casa', '7890000000141', 'UN', 10.00, 24.90, 0, 0, 1, '', 1, 0, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'COMIDAS'), 3),
('Pastel de Queijo', 'Pastel frito na hora recheado com queijo', '7890000000158', 'UN', 3.50, 9.00, 0, 0, 1, '', 1, 0, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'COMIDAS'), 3);

-- 5) BISCOITOS (controlam estoque) --------------------------------------------
INSERT INTO `geficogestor$eclubecampestre_db`.`estoque_produto` (nome, descricao, codigo_barras, unidade, preco_custo, preco_venda, estoque_atual, estoque_minimo, ativo, imagem, exibir_cardapio, controla_estoque, data_criacao, data_atualizacao, categoria_id, empresa_id) VALUES
('Biscoito Cream Cracker', 'Biscoito salgado cream cracker, pacote', '7890000000165', 'UN', 3.00, 6.50, 60, 12, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BISCOITOS'), 3),
('Biscoito Recheado Chocolate', 'Biscoito recheado sabor chocolate, pacote', '7890000000172', 'UN', 2.80, 6.00, 60, 12, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BISCOITOS'), 3),
('Salgadinho de Milho 150g', 'Salgadinho de milho, pacote 150g', '7890000000189', 'UN', 4.50, 9.00, 50, 10, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BISCOITOS'), 3),
('Amendoim Torrado 100g', 'Amendoim torrado e salgado, pacote 100g', '7890000000196', 'UN', 2.50, 5.00, 70, 15, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BISCOITOS'), 3);

-- 6) BOMBONS (controlam estoque) ----------------------------------------------
INSERT INTO `geficogestor$eclubecampestre_db`.`estoque_produto` (nome, descricao, codigo_barras, unidade, preco_custo, preco_venda, estoque_atual, estoque_minimo, ativo, imagem, exibir_cardapio, controla_estoque, data_criacao, data_atualizacao, categoria_id, empresa_id) VALUES
('Caixa de Bombons 250g', 'Caixa de bombons sortidos 250g', '7890000000202', 'UN', 12.00, 24.90, 40, 10, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BOMBONS'), 3),
('Barra de Chocolate ao Leite 90g', 'Barra de chocolate ao leite 90g', '7890000000219', 'UN', 5.00, 10.00, 60, 12, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BOMBONS'), 3),
('Bombom Ouro Branco', 'Bombom ouro branco, unidade', '7890000000226', 'UN', 1.50, 3.50, 150, 30, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BOMBONS'), 3),
('Trufa de Chocolate', 'Trufa de chocolate, unidade', '7890000000233', 'UN', 2.00, 5.00, 100, 20, 1, '', 1, 1, '2026-10-13 10:00:00', '2026-10-13 10:00:00', (SELECT id FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3 AND nome = 'BOMBONS'), 3);

-- 7) CONFERENCIA --------------------------------------------------------------
SELECT 'categorias' AS tipo, COUNT(*) AS qtd FROM `geficogestor$eclubecampestre_db`.`estoque_categoriaproduto` WHERE empresa_id = 3;
SELECT 'produtos' AS tipo, COUNT(*) AS qtd FROM `geficogestor$eclubecampestre_db`.`estoque_produto` WHERE empresa_id = 3;
