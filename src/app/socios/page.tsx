"use client"

import { useState } from "react"
import { LayoutProvider } from "@/components/layout/layout-provider"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
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
  Phone,
  Mail,
  MapPin,
  Calendar,
  Users
} from "lucide-react"
import { SocioForm } from "@/components/socios/socio-form"
import { SocioDetails } from "@/components/socios/socio-details"

// Dados mockados para demonstração
const mockSocios = [
  {
    id: "1",
    nome: "João Silva",
    email: "joao.silva@email.com",
    telefone: "(11) 99999-8888",
    endereco: "Rua das Flores, 123 - São Paulo, SP",
    categoria: "TITULAR",
    status: "ATIVO",
    data_adesao: "2023-01-15",
    dependentes: 2,
  },
  {
    id: "2",
    nome: "Maria Santos",
    email: "maria.santos@email.com",
    telefone: "(11) 99999-7777",
    endereco: "Av. Paulista, 456 - São Paulo, SP",
    categoria: "TITULAR",
    status: "ATIVO",
    data_adesao: "2023-02-20",
    dependentes: 1,
  },
  {
    id: "3",
    nome: "Pedro Oliveira",
    email: "pedro.oliveira@email.com",
    telefone: "(11) 99999-6666",
    endereco: "Rua Augusta, 789 - São Paulo, SP",
    categoria: "DEPENDENTE",
    status: "ATIVO",
    data_adesao: "2023-03-10",
    dependentes: 0,
  },
  {
    id: "4",
    nome: "Ana Costa",
    email: "ana.costa@email.com",
    telefone: "(11) 99999-5555",
    endereco: "Alameda Santos, 321 - São Paulo, SP",
    categoria: "TITULAR",
    status: "INATIVO",
    data_adesao: "2022-12-05",
    dependentes: 3,
  },
]

const getStatusColor = (status: string) => {
  switch (status) {
    case "ATIVO":
      return "bg-green-100 text-green-800"
    case "INATIVO":
      return "bg-red-100 text-red-800"
    case "SUSPENSO":
      return "bg-yellow-100 text-yellow-800"
    default:
      return "bg-gray-100 text-gray-800"
  }
}

const getCategoriaColor = (categoria: string) => {
  switch (categoria) {
    case "TITULAR":
      return "bg-blue-100 text-blue-800"
    case "DEPENDENTE":
      return "bg-purple-100 text-purple-800"
    case "CONTRIBUINTE":
      return "bg-orange-100 text-orange-800"
    case "BENEMERITO":
      return "bg-emerald-100 text-emerald-800"
    default:
      return "bg-gray-100 text-gray-800"
  }
}

export default function SociosPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedSocio, setSelectedSocio] = useState(null)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isDetailsOpen, setIsDetailsOpen] = useState(false)

  const filteredSocios = mockSocios.filter(socio =>
    socio.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    socio.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    socio.cpf?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleEdit = (socio: any) => {
    setSelectedSocio(socio)
    setIsFormOpen(true)
  }

  const handleView = (socio: any) => {
    setSelectedSocio(socio)
    setIsDetailsOpen(true)
  }

  return (
    <ProtectedRoute>
      <LayoutProvider>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Sócios</h1>
              <p className="text-muted-foreground">
                Gerencie os sócios do clube campestre
              </p>
            </div>
            <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Sócio
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>
                    {selectedSocio ? "Editar Sócio" : "Novo Sócio"}
                  </DialogTitle>
                  <DialogDescription>
                    Preencha os dados do sócio
                  </DialogDescription>
                </DialogHeader>
                <SocioForm 
                  socio={selectedSocio}
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
                      Total de Sócios
                    </p>
                    <p className="text-2xl font-bold">{mockSocios.length}</p>
                  </div>
                  <Users className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Sócios Ativos
                    </p>
                    <p className="text-2xl font-bold">
                      {mockSocios.filter(s => s.status === "ATIVO").length}
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
                      Titulares
                    </p>
                    <p className="text-2xl font-bold">
                      {mockSocios.filter(s => s.categoria === "TITULAR").length}
                    </p>
                  </div>
                  <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 text-sm font-bold">T</span>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Dependentes
                    </p>
                    <p className="text-2xl font-bold">
                      {mockSocios.filter(s => s.categoria === "DEPENDENTE").length}
                    </p>
                  </div>
                  <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-purple-600 text-sm font-bold">D</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Search and Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Lista de Sócios</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Buscar sócios..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Table */}
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Sócio</TableHead>
                      <TableHead>Contato</TableHead>
                      <TableHead>Categoria</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Dependentes</TableHead>
                      <TableHead className="w-[100px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredSocios.map((socio) => (
                      <TableRow key={socio.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar className="h-10 w-10">
                              <AvatarFallback>
                                {socio.nome.split(' ').map(n => n[0]).join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <div className="font-medium">{socio.nome}</div>
                              <div className="text-sm text-muted-foreground">
                                Desde {new Date(socio.data_adesao).toLocaleDateString('pt-BR')}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            {socio.email && (
                              <div className="flex items-center gap-1 text-sm">
                                <Mail className="h-3 w-3" />
                                {socio.email}
                              </div>
                            )}
                            {socio.telefone && (
                              <div className="flex items-center gap-1 text-sm">
                                <Phone className="h-3 w-3" />
                                {socio.telefone}
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getCategoriaColor(socio.categoria)}>
                            {socio.categoria}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(socio.status)}>
                            {socio.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Users className="h-3 w-3" />
                            <span className="text-sm">{socio.dependentes}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" className="h-8 w-8 p-0">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => handleView(socio)}>
                                <Eye className="h-4 w-4 mr-2" />
                                Ver detalhes
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleEdit(socio)}>
                                <Edit className="h-4 w-4 mr-2" />
                                Editar
                              </DropdownMenuItem>
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

        {/* Socio Details Dialog */}
        <Dialog open={isDetailsOpen} onOpenChange={setIsDetailsOpen}>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>Detalhes do Sócio</DialogTitle>
            </DialogHeader>
            {selectedSocio && (
              <SocioDetails socio={selectedSocio} />
            )}
          </DialogContent>
        </Dialog>
      </LayoutProvider>
    </ProtectedRoute>
  )
}