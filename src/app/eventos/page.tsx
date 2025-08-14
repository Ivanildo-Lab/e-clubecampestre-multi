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
  Calendar,
  MapPin,
  Users,
  Clock,
  Edit,
  Trash2,
  Eye,
  Filter
} from "lucide-react"
import { EventoForm } from "@/components/eventos/evento-form"

// Dados mockados para demonstração
const eventos = [
  {
    id: "1",
    nome: "Churrasco de Fim de Semana",
    data: "2024-03-15",
    hora: "12:00",
    local: "Área de Churrasco",
    descricao: "Churrasco tradicional para todos os sócios e familiares",
    participantes: 45,
    limite_participantes: 100,
    status: "ABERTO",
    valor: 25.00,
  },
  {
    id: "2",
    nome: "Festa Junina",
    data: "2024-06-15",
    hora: "18:00",
    local: "Salão de Festas",
    descricao: "Festa junina com música, comida típica e quadrilha",
    participantes: 120,
    limite_participantes: 150,
    status: "ABERTO",
    valor: 35.00,
  },
  {
    id: "3",
    nome: "Campeonato de Pesca",
    data: "2024-04-20",
    hora: "06:00",
    local: "Lago Artificial",
    descricao: "Campeonato anual de pesca com premiações",
    participantes: 30,
    limite_participantes: 50,
    status: "ABERTO",
    valor: 50.00,
  },
  {
    id: "4",
    nome: "Reunião de Planejamento",
    data: "2024-03-10",
    hora: "19:00",
    local: "Salão de Reuniões",
    descricao: "Reunião para planejamento das atividades do semestre",
    participantes: 15,
    limite_participantes: 30,
    status: "ENCERRADO",
    valor: 0.00,
  },
]

const getStatusColor = (status: string) => {
  switch (status) {
    case "ABERTO":
      return "bg-green-100 text-green-800"
    case "ENCERRADO":
      return "bg-gray-100 text-gray-800"
    case "CANCELADO":
      return "bg-red-100 text-red-800"
    default:
      return "bg-gray-100 text-gray-800"
  }
}

export default function EventosPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("TODOS")
  const [selectedEvento, setSelectedEvento] = useState(null)
  const [isFormOpen, setIsFormOpen] = useState(false)

  const filteredEventos = eventos.filter(evento => {
    const matchesSearch = evento.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         evento.descricao.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "TODOS" || evento.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const proximosEventos = eventos
    .filter(e => e.status === "ABERTO")
    .sort((a, b) => new Date(a.data).getTime() - new Date(b.data).getTime())
    .slice(0, 3)

  const handleEdit = (evento: any) => {
    setSelectedEvento(evento)
    setIsFormOpen(true)
  }

  return (
    <ProtectedRoute>
      <LayoutProvider>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Eventos</h1>
              <p className="text-muted-foreground">
                Gerencie eventos e atividades do clube
              </p>
            </div>
            <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Evento
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>
                    {selectedEvento ? "Editar Evento" : "Novo Evento"}
                  </DialogTitle>
                  <DialogDescription>
                    Preencha os dados do evento
                  </DialogDescription>
                </DialogHeader>
                <EventoForm 
                  evento={selectedEvento}
                  onSuccess={() => setIsFormOpen(false)}
                />
              </DialogContent>
            </Dialog>
          </div>

          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Total de Eventos
                    </p>
                    <p className="text-2xl font-bold">{eventos.length}</p>
                  </div>
                  <Calendar className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Eventos Abertos
                    </p>
                    <p className="text-2xl font-bold">
                      {eventos.filter(e => e.status === "ABERTO").length}
                    </p>
                  </div>
                  <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-green-600 text-sm font-bold">✓</span>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Participações este mês
                    </p>
                    <p className="text-2xl font-bold">189</p>
                  </div>
                  <Users className="h-8 w-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Próximo Evento
                    </p>
                    <p className="text-2xl font-bold">5 dias</p>
                  </div>
                  <Clock className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Próximos Eventos */}
          <Card>
            <CardHeader>
              <CardTitle>Próximos Eventos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                {proximosEventos.map((evento) => (
                  <div key={evento.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <Badge className={getStatusColor(evento.status)}>
                        {evento.status}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {new Date(evento.data).toLocaleDateString('pt-BR')}
                      </span>
                    </div>
                    <h3 className="font-semibold mb-2">{evento.nome}</h3>
                    <div className="space-y-1 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {evento.hora}
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {evento.local}
                      </div>
                      <div className="flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        {evento.participantes}/{evento.limite_participantes} participantes
                      </div>
                    </div>
                    {evento.valor > 0 && (
                      <div className="mt-2 text-sm font-medium">
                        R$ {evento.valor.toFixed(2)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Lista de Eventos */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Todos os Eventos</CardTitle>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Buscar eventos..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 w-64"
                    />
                  </div>
                  <select 
                    value={statusFilter} 
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-3 py-2 border rounded-md text-sm"
                  >
                    <option value="TODOS">Todos Status</option>
                    <option value="ABERTO">Aberto</option>
                    <option value="ENCERRADO">Encerrado</option>
                    <option value="CANCELADO">Cancelado</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Evento</TableHead>
                      <TableHead>Data e Hora</TableHead>
                      <TableHead>Local</TableHead>
                      <TableHead>Participantes</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="w-[100px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredEventos.map((evento) => (
                      <TableRow key={evento.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{evento.nome}</div>
                            <div className="text-sm text-muted-foreground">
                              {evento.descricao}
                            </div>
                            {evento.valor > 0 && (
                              <div className="text-sm font-medium text-green-600">
                                R$ {evento.valor.toFixed(2)}
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="font-medium">
                              {new Date(evento.data).toLocaleDateString('pt-BR')}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {evento.hora}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <MapPin className="h-3 w-3 text-muted-foreground" />
                            <span>{evento.local}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Users className="h-3 w-3 text-muted-foreground" />
                            <span>{evento.participantes}/{evento.limite_participantes}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(evento.status)}>
                            {evento.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button variant="ghost" size="icon">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => handleEdit(evento)}>
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" className="text-red-600">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
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