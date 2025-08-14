"use client"

import { useState } from "react"
import { LayoutProvider } from "@/components/layout/layout-provider"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { 
  Search, 
  Plus, 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Eye,
  CreditCard,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Calendar,
  Download,
  Filter
} from "lucide-react"
import { MensalidadeForm } from "@/components/financeiro/mensalidade-form"
import { GerarMensalidades } from "@/components/financeiro/gerar-mensalidades"

// Dados mockados para demonstração
const mockMensalidades = [
  {
    id: "1",
    socio_nome: "João Silva",
    socio_email: "joao.silva@email.com",
    valor: 150.00,
    data_vencimento: "2024-03-05",
    status: "PAGO",
    data_pagamento: "2024-03-01",
    forma_pagamento: "PIX",
    juros: 0,
    multa: 0,
  },
  {
    id: "2",
    socio_nome: "Maria Santos",
    socio_email: "maria.santos@email.com",
    valor: 150.00,
    data_vencimento: "2024-03-05",
    status: "PENDENTE",
    data_pagamento: null,
    forma_pagamento: null,
    juros: 0,
    multa: 0,
  },
  {
    id: "3",
    socio_nome: "Pedro Oliveira",
    socio_email: "pedro.oliveira@email.com",
    valor: 100.00,
    data_vencimento: "2024-02-05",
    status: "ATRASADO",
    data_pagamento: null,
    forma_pagamento: null,
    juros: 15.00,
    multa: 10.00,
  },
  {
    id: "4",
    socio_nome: "Ana Costa",
    socio_email: "ana.costa@email.com",
    valor: 150.00,
    data_vencimento: "2024-03-05",
    status: "PAGO",
    data_pagamento: "2024-02-28",
    forma_pagamento: "BOLETO",
    juros: 0,
    multa: 0,
  },
]

const getStatusColor = (status: string) => {
  switch (status) {
    case "PAGO":
      return "bg-green-100 text-green-800"
    case "PENDENTE":
      return "bg-yellow-100 text-yellow-800"
    case "ATRASADO":
      return "bg-red-100 text-red-800"
    case "CANCELADO":
      return "bg-gray-100 text-gray-800"
    default:
      return "bg-gray-100 text-gray-800"
  }
}

export default function FinanceiroPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("TODOS")
  const [selectedMensalidade, setSelectedMensalidade] = useState(null)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isGerarOpen, setIsGerarOpen] = useState(false)

  const filteredMensalidades = mockMensalidades.filter(mensalidade => {
    const matchesSearch = mensalidade.socio_nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mensalidade.socio_email?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "TODOS" || mensalidade.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const totalReceita = mockMensalidades
    .filter(m => m.status === "PAGO")
    .reduce((sum, m) => sum + m.valor, 0)

  const totalPendente = mockMensalidades
    .filter(m => m.status === "PENDENTE")
    .reduce((sum, m) => sum + m.valor, 0)

  const totalAtrasado = mockMensalidades
    .filter(m => m.status === "ATRASADO")
    .reduce((sum, m) => sum + m.valor + m.juros + m.multa, 0)

  const handleEdit = (mensalidade: any) => {
    setSelectedMensalidade(mensalidade)
    setIsFormOpen(true)
  }

  return (
    <ProtectedRoute requiredPermission="FINANCEIRO">
      <LayoutProvider>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Financeiro</h1>
              <p className="text-muted-foreground">
                Gerencie mensalidades e pagamentos dos sócios
              </p>
            </div>
            <div className="flex gap-2">
              <Dialog open={isGerarOpen} onOpenChange={setIsGerarOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <Calendar className="h-4 w-4 mr-2" />
                    Gerar Mensalidades
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Gerar Mensalidades</DialogTitle>
                    <DialogDescription>
                      Gere mensalidades para todos os sócios ativos
                    </DialogDescription>
                  </DialogHeader>
                  <GerarMensalidades onSuccess={() => setIsGerarOpen(false)} />
                </DialogContent>
              </Dialog>
              
              <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Nova Mensalidade
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>
                      {selectedMensalidade ? "Editar Mensalidade" : "Nova Mensalidade"}
                    </DialogTitle>
                    <DialogDescription>
                      Preencha os dados da mensalidade
                    </DialogDescription>
                  </DialogHeader>
                  <MensalidadeForm 
                    mensalidade={selectedMensalidade}
                    onSuccess={() => setIsFormOpen(false)}
                  />
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Total Recebido
                    </p>
                    <p className="text-2xl font-bold">R$ {totalReceita.toFixed(2)}</p>
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
                      A Receber
                    </p>
                    <p className="text-2xl font-bold">R$ {totalPendente.toFixed(2)}</p>
                  </div>
                  <CreditCard className="h-8 w-8 text-blue-600" />
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
                    <p className="text-2xl font-bold">R$ {totalAtrasado.toFixed(2)}</p>
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
                    <p className="text-2xl font-bold">12.5%</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters and Search */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Mensalidades</CardTitle>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Exportar
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Buscar mensalidades..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline">
                      <Filter className="h-4 w-4 mr-2" />
                      {statusFilter === "TODOS" ? "Todos Status" : statusFilter}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuItem onClick={() => setStatusFilter("TODOS")}>
                      Todos Status
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setStatusFilter("PAGO")}>
                      Pago
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setStatusFilter("PENDENTE")}>
                      Pendente
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setStatusFilter("ATRASADO")}>
                      Atrasado
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setStatusFilter("CANCELADO")}>
                      Cancelado
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              {/* Table */}
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Sócio</TableHead>
                      <TableHead>Valor</TableHead>
                      <TableHead>Vencimento</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Pagamento</TableHead>
                      <TableHead className="w-[100px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredMensalidades.map((mensalidade) => (
                      <TableRow key={mensalidade.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{mensalidade.socio_nome}</div>
                            <div className="text-sm text-muted-foreground">
                              {mensalidade.socio_email}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="font-medium">R$ {mensalidade.valor.toFixed(2)}</div>
                          {(mensalidade.juros > 0 || mensalidade.multa > 0) && (
                            <div className="text-xs text-red-600">
                              + Juros: R$ {mensalidade.juros.toFixed(2)} + Multa: R$ {mensalidade.multa.toFixed(2)}
                            </div>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="font-medium">
                            {new Date(mensalidade.data_vencimento).toLocaleDateString('pt-BR')}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(mensalidade.status)}>
                            {mensalidade.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {mensalidade.data_pagamento ? (
                            <div>
                              <div className="text-sm">
                                {new Date(mensalidade.data_pagamento).toLocaleDateString('pt-BR')}
                              </div>
                              {mensalidade.forma_pagamento && (
                                <div className="text-xs text-muted-foreground">
                                  {mensalidade.forma_pagamento}
                                </div>
                              )}
                            </div>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" className="h-8 w-8 p-0">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => handleEdit(mensalidade)}>
                                <Edit className="h-4 w-4 mr-2" />
                                Editar
                              </DropdownMenuItem>
                              {mensalidade.status !== "PAGO" && (
                                <DropdownMenuItem>
                                  <CreditCard className="h-4 w-4 mr-2" />
                                  Registrar Pagamento
                                </DropdownMenuItem>
                              )}
                              <DropdownMenuItem className="text-red-600">
                                <Trash2 className="h-4 w-4 mr-2" />
                                Excluir
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      </LayoutProvider>
    </ProtectedRoute>
  )
}