import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"
import bcrypt from "bcryptjs"

export async function POST(request: NextRequest) {
  try {
    const { nome, email, password, nivel_permissao = "ATENDIMENTO" } = await request.json()

    if (!nome || !email || !password) {
      return NextResponse.json(
        { error: "Nome, email e senha são obrigatórios" },
        { status: 400 }
      )
    }

    // Verificar se o email já existe
    const usuarioExistente = await db.usuario.findUnique({
      where: { email }
    })

    if (usuarioExistente) {
      return NextResponse.json(
        { error: "Email já cadastrado" },
        { status: 400 }
      )
    }

    // Hash da senha
    const senha_hash = await bcrypt.hash(password, 10)

    // Criar usuário
    const usuario = await db.usuario.create({
      data: {
        nome,
        email,
        senha_hash,
        nivel_permissao
      }
    })

    // Retornar dados do usuário (sem a senha)
    const { senha_hash: _, ...usuarioSemSenha } = usuario

    return NextResponse.json({
      message: "Usuário criado com sucesso",
      usuario: usuarioSemSenha
    })

  } catch (error) {
    console.error("Erro no registro:", error)
    return NextResponse.json(
      { error: "Erro interno do servidor" },
      { status: 500 }
    )
  }
}