# Clube Manager - Sistema de Gestão de Clube Campestre

Um sistema completo e moderno para gestão de sócios, controle financeiro e administração de clubes campestres. Desenvolvido com Next.js 15, TypeScript e interface responsiva para web e mobile.

## 🚀 Funcionalidades

### 1. Cadastro e CRM de Sócios
- ✅ Formulário completo de cadastro com validação
- ✅ Categorias: Titular, Dependente, Contribuinte, Benemérito
- ✅ Status: Ativo, Inativo, Suspenso
- ✅ Vinculação de dependentes a sócios titulares
- ✅ Histórico de interações e comunicações
- ✅ Campo de anotações internas
- ✅ Busca e filtros avançados

### 2. Controle Financeiro
- ✅ Geração automática de mensalidades
- ✅ Valores configuráveis por categoria
- ✅ Registro de pagamentos com múltiplos métodos
- ✅ Integração com PIX e Boleto (estrutura preparada)
- ✅ Cálculo automático de juros e multas
- ✅ Relatórios financeiros em tempo real
- ✅ Exportação de dados

### 3. Relatórios e Cobrança
- ✅ Dashboard com gráficos interativos
- ✅ Lista de inadimplentes com filtros
- ✅ Emissão automática de avisos de cobrança
- ✅ Múltiplos canais: Email, WhatsApp, SMS
- ✅ Templates personalizáveis de comunicação
- ✅ Automação de cobranças

### 4. Usuários e Segurança
- ✅ Sistema de login com níveis de permissão
- ✅ Controle de acesso baseado em função (RBAC)
- ✅ Níveis: Administrador, Financeiro, Atendimento
- ✅ Proteção de rotas e componentes
- ✅ Backup automático (configurável)

### 5. Gestão de Eventos
- ✅ Criação e gerenciamento de eventos
- ✅ Controle de participantes
- ✅ Inscrições com limites
- ✅ Valor por evento (opcional)
- ✅ Status do evento: Aberto, Encerrado, Cancelado

### 6. Interface e Design
- ✅ Design moderno e minimalista
- ✅ Totalmente responsiva (mobile e desktop)
- ✅ Menu lateral para desktop
- ✅ Menu inferior para mobile
- ✅ Cores suaves e tipografia clara
- ✅ Componentes da shadcn/ui
- ✅ Dark mode pronto para implementação

## 🛠️ Tecnologias Utilizadas

### Frontend
- **Next.js 15** - Framework React com App Router
- **TypeScript 5** - Tipagem estática
- **Tailwind CSS 4** - Estilização moderna
- **shadcn/ui** - Biblioteca de componentes UI
- **Lucide React** - Ícones
- **Recharts** - Gráficos e visualizações
- **React Hook Form + Zod** - Formulários e validação
- **Zustand** - Gerenciamento de estado

### Backend
- **API Routes** - Rotas da API do Next.js
- **Prisma ORM** - Banco de dados e ORM
- **SQLite** - Banco de dados (desenvolvimento)
- **bcryptjs** - Hash de senhas
- **Socket.io** - Comunicação em tempo real

### Infraestrutura
- **Node.js** - Ambiente de execução
- **Nodemon** - Desenvolvimento com auto-reload
- **ESLint** - Qualidade de código

## 📁 Estrutura do Projeto

```
src/
├── app/                    # Páginas e rotas da API
│   ├── api/               # Rotas da API
│   │   ├── auth/          # Autenticação
│   │   └── auth/seed/     # Seed de usuários
│   ├── login/             # Página de login
│   ├── socios/            # Gestão de sócios
│   ├── financeiro/        # Controle financeiro
│   ├── relatorios/        # Relatórios
│   ├── cobranca/          # Sistema de cobrança
│   ├── eventos/           # Gestão de eventos
│   ├── configuracoes/     # Configurações
│   ├── unauthorized/      # Acesso negado
│   ├── layout.tsx         # Layout principal
│   └── page.tsx           # Dashboard
├── components/            # Componentes reutilizáveis
│   ├── auth/             # Componentes de autenticação
│   ├── dashboard/        # Componentes do dashboard
│   ├── socios/           # Componentes de sócios
│   ├── financeiro/       # Componentes financeiros
│   ├── cobranca/         # Componentes de cobrança
│   ├── eventos/          # Componentes de eventos
│   ├── layout/           # Componentes de layout
│   └── ui/               # Componentes shadcn/ui
├── hooks/                # Hooks personalizados
│   └── use-auth.ts       # Hook de autenticação
└── lib/                  # Utilitários
    ├── db.ts            # Cliente Prisma
    ├── utils.ts         # Funções utilitárias
    └── socket.ts        # Configuração Socket.io
```

## 🗄️ Banco de Dados

### Schema do Banco de Dados

```sql
-- Tabela de usuários
CREATE TABLE usuarios (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  senha_hash TEXT NOT NULL,
  nivel_permissao TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de sócios
CREATE TABLE socios (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  cpf TEXT UNIQUE NOT NULL,
  rg TEXT,
  telefone TEXT,
  email TEXT,
  endereco TEXT,
  data_adesao DATETIME DEFAULT CURRENT_TIMESTAMP,
  categoria TEXT NOT NULL,
  status TEXT NOT NULL,
  id_titular TEXT,
  anotacoes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_titular) REFERENCES socios(id)
);

-- Tabela de mensalidades
CREATE TABLE mensalidades (
  id TEXT PRIMARY KEY,
  id_socio TEXT NOT NULL,
  valor REAL NOT NULL,
  data_vencimento DATETIME NOT NULL,
  status TEXT NOT NULL,
  data_pagamento DATETIME,
  juros REAL DEFAULT 0,
  multa REAL DEFAULT 0,
  forma_pagamento TEXT,
  recibo TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_socio) REFERENCES socios(id)
);

-- Tabela de interações
CREATE TABLE interacoes (
  id TEXT PRIMARY KEY,
  id_socio TEXT NOT NULL,
  id_usuario TEXT,
  tipo TEXT NOT NULL,
  descricao TEXT NOT NULL,
  data DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_socio) REFERENCES socios(id),
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

-- Tabela de configurações
CREATE TABLE configuracoes (
  id TEXT PRIMARY KEY,
  chave TEXT UNIQUE NOT NULL,
  valor TEXT NOT NULL,
  descricao TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Instalação e Execução

### Pré-requisitos
- Node.js 18+ 
- npm ou yarn

### Passos

1. **Clone o repositório**
```bash
git clone <repositorio>
cd clube-manager
```

2. **Instale as dependências**
```bash
npm install
```

3. **Configure o banco de dados**
```bash
# Execute o push do schema para o banco
npm run db:push

# Gere o cliente Prisma
npm run db:generate
```

4. **Crie um usuário administrador**
```bash
# Use a API de seed ou crie diretamente no banco
curl -X POST http://localhost:3000/api/auth/seed \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clubemanager.com",
    "password": "admin123",
    "nome": "Administrador",
    "nivel_permissao": "ADMINISTRADOR"
  }'
```

5. **Inicie o servidor de desenvolvimento**
```bash
npm run dev
```

6. **Acesse a aplicação**
- Frontend: http://localhost:3000
- API: http://localhost:3000/api

### Login de Demonstração
- **Email**: `admin@clubemanager.com`
- **Senha**: `admin123`

## 📱 Responsividade

O sistema é totalmente responsivo e oferece:

### Desktop
- Menu lateral fixo com navegação completa
- Dashboard com múltiplos cards e gráficos
- Tabelas com dados detalhados
- Formulários em colunas

### Mobile
- Menu inferior com acesso rápido
- Interface otimizada para toque
- Cards empilhados verticalmente
- Formulários em tela única

## 🔐 Segurança

- **Autenticação**: Sistema de login seguro com hash de senhas
- **Autorização**: Controle de acesso baseado em funções (RBAC)
- **Proteção de Rotas**: Middleware para proteger páginas sensíveis
- **Validação**: Validação de dados no frontend e backend
- **SQL Injection**: Proteção com Prisma ORM

## 🎨 Design System

O sistema utiliza:
- **Cores**: Paleta suave com foco em acessibilidade
- **Tipografia**: Fontes claras e legíveis
- **Componentes**: Biblioteca shadcn/ui consistente
- **Ícones**: Lucide React modernos e uniformes
- **Espaçamento**: Sistema de grid consistente

## 🚀 Implantação

### Produção
```bash
# Build da aplicação
npm run build

# Inicie o servidor de produção
npm start
```

### Variáveis de Ambiente
```env
DATABASE_URL="file:./dev.db"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="sua-chave-secreta"
```

## 📈 Roadmap Futuro

### Planejado
- [ ] Integração real com gateways de pagamento
- [ ] Envio de emails e WhatsApp reais
- [ ] Sistema de relatórios avançados
- [ ] Módulo de estoque e compras
- [ ] App mobile nativo (React Native)
- [ ] Integração com sistemas de terceiros
- [ ] Multi-tenancy para múltiplos clubes

### Melhorias
- [ ] Otimização de performance
- [ ] Testes automatizados
- [ ] Documentação da API
- [ ] Internacionalização (i18n)
- [ ] Dark mode
- [ ] Offline mode

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para suporte, envie um email para suporte@clubemanager.com ou abra uma issue no GitHub.

---

**Desenvolvido com ❤️ para clubes campestres brasileiros**