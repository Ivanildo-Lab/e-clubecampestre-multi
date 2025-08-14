"use client"

import { useState } from "react"
import { LayoutProvider } from "@/components/layout/layout-provider"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { 
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts"
import { 
  Download, 
  Filter, 
  Calendar, 
  TrendingUp, 
  TrendingDown,
  Users,
  DollarSign,
  AlertTriangle,
  FileText,
  Mail,
  MessageSquare,
  Phone
} from "lucide-react"

// Dados mockados para demonstração
const receitaData = [
  { month: "Jan", receita: 40000, despesas: 24000 },
  { month: "Fev", receita: 30000, despesas: 13980 },
  { month: "Mar", receita: 98000, despesas: 20000 },
  { month: "Abr", receita: 39080, despesas: 27800 },
  { month: "Mai", receita: 48000, despesas: 18900 },
  { month: "Jun", receita: 38000, despesas: 23900 },
]

const inadimplenciaData = [
  { name: "0-30 dias", value: 15, color: "#fbbf24" },
  { name: "31-60 dias", value: 8, color: "#f87171" },
  { name: "61-90 dias", value: 4, color: "#dc2626" },
  { name: "+90 dias", value: 2, color: "#991b1b" },
]

const categoriaData = [
  { name: "Titular", value: 45, color: "#3b82f6" },
  { name: "Dependente", value: 25, color: "#8b5cf6" },
  { name: "Contribuinte", value: 20, color: "#f59e0b" },
  { name: "Benemérito", value: 10, color: "#10b981" },
]

const inadimplentes = [
  {
    id: "1",
    nome: "Carlos Alberto",
    email: "carlos@email.com",
    telefone: "(11) 99999-8888",
    valor: 150.00,
    dias_atraso: 15,
    categoria: "Titular",
  },
  {
    id: "2",
    nome: "Ana Paula",
    email: "ana@email.com",
    telefone: "(11) 99999-7777",
    valor: 300.00,
    dias_atraso: 30,
    categoria: "Titular",
  },
  {
    id: "3",
    nome: "Roberto Silva",
    email: "roberto@email.com",
    telefone: "(11) 99999-6666",
    valor: 150.00,
    dias_atraso: 45,
    categoria: "Dependente",
  },
  {
    id: "4",
    nome: "Fernanda Costa",
    email: "fernanda@email.com",
    telefone: "(11) 99999-5555",
    valor: 450.00,
    dias_atraso: 60,
    categoria: "Titular",
  },
]

export default function RelatoriosPage() {
  const [dateRange, setDateRange] = useState("last_30_days")
  const [selectedInadimplentes, setSelectedInadimplentes] = useState<string[]>([])

  const totalReceita = receitaData.reduce((sum, item) => sum + item.receita, 0)
  const totalDespesas = receitaData.reduce((sum, item) => sum + item.despesas, 0)
  const totalInadimplencia = inadimplentes.reduce((sum, item) => sum + item.valor, 0)

  const handleSelectAll = () => {
    if (selectedInadimplentes.length === inadimplentes.length) {
      setSelectedInadimplentes([])
    } else {
      setSelectedInadimplentes(inadimplentes.map(i => i.id))
    }
  }

  const handleSelectInadimplente = (id: string) => {
    setSelectedInadimplentes(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id)
        : [...prev, id]
    )
  }

  const handleSendNotification = (type: 'email' | 'whatsapp' | 'sms') => {
    console.log(`Enviando ${type} para:`, selectedInadimplentes)
    // Aqui seria implementado o envio real
  }

  return (
    <ProtectedRoute requiredPermission="FINANCEIRO">
      <LayoutProvider>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Relatórios</h1>
              <p className="text-muted-foreground">
                Análise financeira e relatórios de inadimplência
              </p>
            </div>
            <div className="flex gap-2">
              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger className="w-[200px]">
                  <Calendar className="h-4 w-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="last_7_days">Últimos 7 dias</SelectItem>
                  <SelectItem value="last_30_days">Últimos 30 dias</SelectItem>
                  <SelectItem value="last_90_days">Últimos 90 dias</SelectItem>
                  <SelectItem value="this_year">Este ano</SelectItem>
                  <SelectItem value="custom">Personalizado</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>

          {/* KPIs */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Receita Total
                    </p>
                    <p className="text-2xl font-bold">R$ {totalReceita.toLocaleString('pt-BR')}</p>
                    <div className="flex items-center gap-1 text-green-600 text-sm">
                      <TrendingUp className="h-3 w-3" />
                      +12%
                    </div>
                  </div>
                  <DollarSign className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Despesas Totais
                    </p>
                    <p className="text-2xl font-bold">R$ {totalDespesas.toLocaleString('pt-BR')}</p>
                    <div className="flex items-center gap-1 text-red-600 text-sm">
                      <TrendingDown className="h-3 w-3" />
                      +5%
                    </div>
                  </div>
                  <FileText className="h-8 w-8 text-red-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Inadimplência
                    </p>
                    <p className="text-2xl font-bold">R$ {totalInadimplencia.toLocaleString('pt-BR')}</p>
                    <div className="flex items-center gap-1 text-red-600 text-sm">
                      <TrendingUp className="h-3 w-3" />
                      +8%
                    </div>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-red-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Taxa de Inadimplência
                    </p>
                    <p className="text-2xl font-bold">5.2%</p>
                    <div className="flex items-center gap-1 text-green-600 text-sm">
                      <TrendingDown className="h-3 w-3" />
                      -2%
                    </div>
                  </div>
                  <Users className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <Tabs defaultValue="financeiro" className="space-y-4">
            <TabsList>
              <TabsTrigger value="financeiro">Financeiro</TabsTrigger>
              <TabsTrigger value="inadimplencia">Inadimplência</TabsTrigger>
              <TabsTrigger value="socios">Sócios</TabsTrigger>
              <TabsTrigger value="cobranca">Cobrança</TabsTrigger>
            </TabsList>

            <TabsContent value="financeiro">
              <div className="grid gap-6 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Receita vs Despesas</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={receitaData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="receita" fill="#10b981" name="Receita" />
                        <Bar dataKey="despesas" fill="#ef4444" name="Despesas" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Evolução da Receita</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={receitaData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Line 
                          type="monotone" 
                          dataKey="receita" 
                          stroke="#3b82f6" 
                          strokeWidth={2}
                          name="Receita"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="inadimplencia">
              <div className="grid gap-6 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Inadimplência por Período</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={inadimplenciaData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {inadimplenciaData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Distribuição por Categoria</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={categoriaData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {categoriaData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="socios">
              <Card>
                <CardHeader>
                  <CardTitle>Estatísticas de Sócios</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">156</div>
                      <div className="text-sm text-muted-foreground">Total de Sócios</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-green-600">142</div>
                      <div className="text-sm text-muted-foreground">Sócios Ativos</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">45</div>
                      <div className="text-sm text-muted-foreground">Novos este mês</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="cobranca">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Lista de Inadimplentes</CardTitle>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={selectedInadimplentes.length === 0}
                        onClick={() => handleSendNotification('email')}
                      >
                        <Mail className="h-4 w-4 mr-2" />
                        Enviar Email
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={selectedInadimplentes.length === 0}
                        onClick={() => handleSendNotification('whatsapp')}
                      >
                        <MessageSquare className="h-4 w-4 mr-2" />
                        Enviar WhatsApp
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={selectedInadimplentes.length === 0}
                        onClick={() => handleSendNotification('sms')}
                      >
                        <Phone className="h-4 w-4 mr-2" />
                        Enviar SMS
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 p-2 border-b">
                      <input
                        type="checkbox"
                        checked={selectedInadimplentes.length === inadimplentes.length}
                        onChange={handleSelectAll}
                        className="rounded"
                      />
                      <span className="text-sm font-medium">
                        {selectedInadimplentes.length} de {inadimplentes.length} selecionados
                      </span>
                    </div>
                    
                    {inadimplentes.map((inadimplente) => (
                      <div key={inadimplente.id} className="flex items-center gap-3 p-3 border rounded-lg">
                        <input
                          type="checkbox"
                          checked={selectedInadimplentes.includes(inadimplente.id)}
                          onChange={() => handleSelectInadimplente(inadimplente.id)}
                          className="rounded"
                        />
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium">{inadimplente.nome}</div>
                              <div className="text-sm text-muted-foreground">
                                {inadimplente.email} • {inadimplente.telefone}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-medium text-red-600">
                                R$ {inadimplente.valor.toFixed(2)}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {inadimplente.dias_atraso} dias atrasado
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge variant="outline">{inadimplente.categoria}</Badge>
                            <Badge variant="destructive">
                              {inadimplente.dias_atraso} dias
                            </Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </LayoutProvider>
    </ProtectedRoute>
  )
}