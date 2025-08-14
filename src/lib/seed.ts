import { db } from "./db"
import bcrypt from "bcryptjs"

async function seed() {
  try {
    console.log("Iniciando seed do banco de dados...")

    // Criar usuário administrador padrão
    const adminPassword = await bcrypt.hash("admin123", 10)
    
    const admin = await db.usuario.upsert({
      where: { email: "admin@clubemanager.com" },
      update: {},
      create: {
        nome: "Administrador",
        email: "admin@clubemanager.com",
        senha_hash: adminPassword,
        nivel_permissao: "ADMINISTRADOR"
      }
    })

    console.log("Usuário administrador criado:", admin.email)

    // Criar usuário financeiro
    const financeiroPassword = await bcrypt.hash("financeiro123", 10)
    
    const financeiro = await db.usuario.upsert({
      where: { email: "financeiro@clubemanager.com" },
      update: {},
      create: {
        nome: "Financeiro",
        email: "financeiro@clubemanager.com",
        senha_hash: financeiroPassword,
        nivel_permissao: "FINANCEIRO"
      }
    })

    console.log("Usuário financeiro criado:", financeiro.email)

    // Criar usuário atendimento
    const atendimentoPassword = await bcrypt.hash("atendimento123", 10)
    
    const atendimento = await db.usuario.upsert({
      where: { email: "atendimento@clubemanager.com" },
      update: {},
      create: {
        nome: "Atendimento",
        email: "atendimento@clubemanager.com",
        senha_hash: atendimentoPassword,
        nivel_permissao: "ATENDIMENTO"
      }
    })

    console.log("Usuário atendimento criado:", atendimento.email)

    // Criar configurações padrão
    await db.configuracao.upsert({
      where: { chave: "valor_mensalidade_titular" },
      update: {},
      create: {
        chave: "valor_mensalidade_titular",
        valor: "150.00",
        descricao: "Valor da mensalidade para sócios titulares"
      }
    })

    await db.configuracao.upsert({
      where: { chave: "valor_mensalidade_dependente" },
      update: {},
      create: {
        chave: "valor_mensalidade_dependente",
        valor: "75.00",
        descricao: "Valor da mensalidade para sócios dependentes"
      }
    })

    await db.configuracao.upsert({
      where: { chave: "juros_atraso" },
      update: {},
      create: {
        chave: "juros_atraso",
        valor: "2.00",
        descricao: "Percentual de juros por atraso"
      }
    })

    await db.configuracao.upsert({
      where: { chave: "multa_atraso" },
      update: {},
      create: {
        chave: "multa_atraso",
        valor: "5.00",
        descricao: "Percentual de multa por atraso"
      }
    })

    console.log("Configurações padrão criadas")

    console.log("Seed concluído com sucesso!")

  } catch (error) {
    console.error("Erro no seed:", error)
    process.exit(1)
  }
}

seed()
  .then(() => {
    process.exit(0)
  })
  .catch((error) => {
    console.error(error)
    process.exit(1)
  })