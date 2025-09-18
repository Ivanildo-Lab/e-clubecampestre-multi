-- ===================================================================
-- SCRIPT COMPLETO E FINAL PARA POPULAR O BANCO DE DADOS
-- ===================================================================

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE core_dependente; TRUNCATE TABLE financeiro_mensalidade; TRUNCATE TABLE financeiro_conta; TRUNCATE TABLE financeiro_lancamentocaixa;
TRUNCATE TABLE core_socio; TRUNCATE TABLE core_categoriassocio; TRUNCATE TABLE core_convenio; TRUNCATE TABLE core_empresa;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. EMPRESAS
INSERT INTO `core_empresa` (`nome`, `responsavel`) VALUES
('GEFICO', 'Ivanildo'),
('CLUBE AMERICA', 'Ivanildo');

-- 2. CATEGORIAS DE SÓCIO
INSERT INTO core_categoriassocio (empresa_id, nome, valor_mensalidade, dia_vencimento) VALUES
(1, 'Plano Ouro GEFICO', 250.00, 10),
(1, 'Plano Prata GEFICO', 180.00, 15),
(2, 'Sócio Campeão AMERICA', 300.00, 5),
(2, 'Sócio Torcedor AMERICA', 150.00, 20);

-- 3. CONVÊNIOS
INSERT INTO core_convenio (empresa_id, nome) VALUES (1, 'Nenhum GEFICO'), (2, 'Nenhum AMERICA');

-- 4. SÓCIOS
INSERT INTO core_socio (empresa_id, num_registro, num_contrato, categoria_id, convenio_id, nome, apelido, data_nascimento, cpf, rg, nacionalidade, naturalidade, estado_civil, profissao, nome_pai, nome_mae, email, tel_residencial, tel_trabalho, endereco, bairro, cidade, estado, cep, data_admissao, situacao, foto, observacoes) VALUES
(1, 2001, 101, 1, 1, 'Ana Clara Ribeiro (GEFICO)', 'Aninha', '1990-01-01', '101.101.101-01', '', 'Brasileira', '', 'CASADO', '', '', '', 'ana.clara@emailgefico.com', '', '', '', '', '', '', '', '2020-01-15', 'ATIVO', '', ''),
(1, 2002, 102, 2, 1, 'Bruno Costa e Silva (GEFICO)', 'Bruno', '1988-02-02', '102.102.102-02', '', 'Brasileira', '', 'SOLTEIRO', '', '', '', NULL, '', '', '', '', '', '', '', '2021-02-20', 'ATIVO', '', ''),
(2, 3001, 201, 3, 2, 'David Nogueira (AMERICA)', '', '1985-04-04', '201.201.201-01', '', 'Brasileira', '', 'CASADO', '', '', '', 'david.nogueira@emailamerica.com', '', '', '', '', '', '', '', '2019-04-10', 'ATIVO', '', ''),
(2, 3002, 202, 4, 2, 'Eduarda Matos (AMERICA)', 'Duda', '1992-05-05', '202.202.202-02', '', 'Brasileira', '', 'SOLTEIRO', '', '', '', NULL, '', '', '', '', '', '', '', '2023-05-15', 'ATIVO', '', '');

-- 5. DEPENDENTES (COM BUSCA DINÂMICA DE ID)
INSERT INTO core_dependente (socio_titular_id, nome, data_nascimento, parentesco, cpf, foto) VALUES
-- Dependente de Ana Clara (busca o ID do sócio com o CPF correspondente)
((SELECT id FROM core_socio WHERE cpf = '101.101.101-01'), 'Marcos Ribeiro Junior', '2018-05-05', 'FILHO', NULL, ''),

-- Dependentes de David Nogueira (busca o ID do sócio com o CPF correspondente)
((SELECT id FROM core_socio WHERE cpf = '201.201.201-01'), 'Helena Nogueira', '2015-07-07', 'FILHO', NULL, ''),
((SELECT id FROM core_socio WHERE cpf = '201.201.201-01'), 'Isabela Nogueira', '2017-08-08', 'FILHO', NULL, '');