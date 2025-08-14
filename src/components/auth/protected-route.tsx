"use client"

import { useAuth } from "@/hooks/auth-context"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { Loader2 } from "lucide-react"

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredPermission?: "ADMINISTRADOR" | "FINANCEIRO" | "ATENDIMENTO"
}

export function ProtectedRoute({ children, requiredPermission }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (user && requiredPermission) {
      const permissions = {
        ADMINISTRADOR: ["ADMINISTRADOR", "FINANCEIRO", "ATENDIMENTO"],
        FINANCEIRO: ["FINANCEIRO", "ATENDIMENTO"],
        ATENDIMENTO: ["ATENDIMENTO"]
      }

      if (!permissions[requiredPermission].includes(user.nivel_permissao)) {
        router.push("/unauthorized")
      }
    }
  }, [user, requiredPermission, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (!user) {
    return null
  }

  if (requiredPermission) {
    const permissions = {
      ADMINISTRADOR: ["ADMINISTRADOR", "FINANCEIRO", "ATENDIMENTO"],
      FINANCEIRO: ["FINANCEIRO", "ATENDIMENTO"],
      ATENDIMENTO: ["ATENDIMENTO"]
    }

    if (!permissions[requiredPermission].includes(user.nivel_permissao)) {
      return null
    }
  }

  return <>{children}</>
}