import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"
import bcrypt from "bcryptjs"

export async function POST(request: NextRequest) {
  try {
    const { email, password, nome, nivel_permissao } = await request.json()

    if (!email || !password || !nome) {
      return NextResponse.json(
        { error: "Email, senha e nome são obrigatórios" },
        { status: 400 }
      )
    }

    // Verificar se usuário já existe
    const existingUser = await db.usuario.findUnique({
      where: { email }
    })

    if (existingUser) {
      return NextResponse.json(
        { error: "Usuário já existe" },
        { status: 400 }
      )
    }

    // Hash da senha
    const senha_hash = await bcrypt.hash(password, 10)

    // Criar usuário
    const usuario = await db.usuario.create({
      data: {
        email,
        senha_hash,
        nome,
        nivel_permissao: nivel_permissao || "ATENDIMENTO"
      }
    })

    // Retornar dados do usuário (sem a senha)
    const { senha_hash: _, ...usuarioSemSenha } = usuario

    return NextResponse.json({
      message: "Usuário criado com sucesso",
      usuario: usuarioSemSenha
    })

  } catch (error) {
    console.error("Erro ao criar usuário:", error)
    return NextResponse.json(
      { error: "Erro interno do servidor" },
      { status: 500 }
    )
  }
}