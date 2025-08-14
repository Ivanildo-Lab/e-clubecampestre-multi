"use client"

import { LayoutProvider } from "@/components/layout/layout-provider"
import { StatsCard } from "@/components/dashboard/stats-card"
import { RevenueChart } from "@/components/dashboard/revenue-chart"
import { RecentActivities } from "@/components/dashboard/recent-activities"
import { OverdueMembers } from "@/components/dashboard/overdue-members"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { 
  Users, 
  DollarSign, 
  TrendingUp, 
  AlertTriangle,
  CreditCard,
  Calendar
} from "lucide-react"

export default function Home() {
  return (
    <ProtectedRoute>
      <LayoutProvider>
        <div className="space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              Bem-vindo ao sistema de gestão do clube campestre
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatsCard
              title="Total de Sócios"
              value="1,234"
              description="+12% em relação ao mês anterior"
              icon={<Users className="h-4 w-4 text-muted-foreground" />}
              trend="up"
              trendValue="12%"
            />
            <StatsCard
              title="Receita Mensal"
              value="R$ 45.231"
              description="+8% em relação ao mês anterior"
              icon={<DollarSign className="h-4 w-4 text-muted-foreground" />}
              trend="up"
              trendValue="8%"
            />
            <StatsCard
              title="Inadimplência"
              value="5.2%"
              description="-2% em relação ao mês anterior"
              icon={<TrendingUp className="h-4 w-4 text-muted-foreground" />}
              trend="down"
              trendValue="2%"
            />
            <StatsCard
              title="Pagamentos Pendentes"
              value="23"
              description="5 com mais de 30 dias"
              icon={<AlertTriangle className="h-4 w-4 text-muted-foreground" />}
              trend="neutral"
            />
          </div>

          {/* Charts and Lists */}
          <div className="grid gap-6 md:grid-cols-2">
            <RevenueChart />
            <RecentActivities />
          </div>

          {/* Overdue Members */}
          <OverdueMembers />

          {/* Quick Actions */}
          <div className="grid gap-4 md:grid-cols-3">
            <div className="p-6 border rounded-lg">
              <div className="flex items-center gap-2 mb-4">
                <Users className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-semibold">Novo Sócio</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Cadastre um novo sócio no sistema
              </p>
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
                Cadastrar Sócio
              </button>
            </div>

            <div className="p-6 border rounded-lg">
              <div className="flex items-center gap-2 mb-4">
                <CreditCard className="h-5 w-5 text-green-600" />
                <h3 className="text-lg font-semibold">Gerar Mensalidades</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Gere as mensalidades do mês atual
              </p>
              <button className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors">
                Gerar Mensalidades
              </button>
            </div>

            <div className="p-6 border rounded-lg">
              <div className="flex items-center gap-2 mb-4">
                <Calendar className="h-5 w-5 text-purple-600" />
                <h3 className="text-lg font-semibold">Novo Evento</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Crie um novo evento para os sócios
              </p>
              <button className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors">
                Criar Evento
              </button>
            </div>
          </div>
        </div>
      </LayoutProvider>
    </ProtectedRoute>
  )
}