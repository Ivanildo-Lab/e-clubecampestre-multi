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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
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
  Filter, 
  Calendar, 
  Send,
  MessageSquare,
  Mail,
  Phone,
  Bell,
  CheckCircle,
  AlertTriangle,
  Clock,
  Users,
  FileText,
  Download
} from "lucide-react"
import { CobrancaForm } from "@/components/cobranca/cobranca-form"
import { TemplateCobranca } from "@/components/cobranca/template-cobranca"

// Dados mockados para demonstração
const inadimplentes = [
  {
    id: "1",
    nome: "Carlos Alberto",
    email: "carlos@email.com",
    telefone: "(11) 99999-8888",
    valor: 150.00,
    dias_atraso: 15,
    categoria: "Titular",
    ultimo_contato: "2024-03-01",
    status_envio: "ENVIADO",
  },
  {
    id: "2",
    nome: "Ana Paula",
    email: "ana@email.com",
    telefone: "(11) 99999-7777",
    valor: 300.00,
    dias_atraso: 30,
    categoria: "Titular",
    ultimo_contato: "2024-02-28",
    status_envio: "PENDENTE",
  },
  {
    id: "3",
    nome: "Roberto Silva",
    email: "roberto@email.com",
    telefone: "(11) 99999-6666",
    valor: 150.00,
    dias_atraso: 45,
    categoria: "Dependente",
    ultimo_contato: "2024-02-15",
    status_envio: "ENVIADO",
  },
  {
    id: "4",
    nome: "Fernanda Costa",
    email: "fernanda@email.com",
    telefone: "(11) 99999-5555",
    valor: 450.00,
    dias_atraso: 60,
    categoria: "Titular",
    ultimo_contato: "2024-02-01",
    status_envio: "PENDENTE",
  },
]

const historicoCobranca = [
  {
    id: "1",
    socio_nome: "Carlos Alberto",
    tipo: "EMAIL",
    mensagem: "Lembrete de pagamento - Mensalidade em atraso",
    data_envio: "2024-03-01 10:30",
    status: "ENVIADO",
  },
  {
    id: "2",
    socio_nome: "Ana Paula",
    tipo: "WHATSAPP",
    mensagem: "Cobrança - 30 dias de atraso",
    data_envio: "2024-02-28 14:15",
    status: "ENVIADO",
  },
  {
    id: "3",
    socio_nome: "Roberto Silva",
    tipo: "SMS",
    mensagem: "Pagamento pendente - 45 dias",
    data_envio: "2024-02-15 09:00",
    status: "FALHOU",
  },
  {
    id: "4",
    socio_nome: "Fernanda Costa",
    tipo: "EMAIL",
    mensagem: "Notificação de inadimplência",
    data_envio: "2024-02-01 16:45",
    status: "ENVIADO",
  },
]

const getStatusColor = (status: string) => {
  switch (status) {
    case "ENVIADO":
      return "bg-green-100 text-green-800"
    case "PENDENTE":
      return "bg-yellow-100 text-yellow-800"
    case "FALHOU":
      return "bg-red-100 text-red-800"
    default:
      return "bg-gray-100 text-gray-800"
  }
}

const getTipoIcon = (tipo: string) => {
  switch (tipo) {
    case "EMAIL":
      return <Mail className="h-4 w-4" />
    case "WHATSAPP":
      return <MessageSquare className="h-4 w-4" />
    case "SMS":
      return <Phone className="h-4 w-4" />
    default:
      return <Send className="h-4 w-4" />
  }
}

export default function CobrancaPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("TODOS")
  const [selectedInadimplentes, setSelectedInadimplentes] = useState<string[]>([])
  const [isCobrancaOpen, setIsCobrancaOpen] = useState(false)
  const [isTemplateOpen, setIsTemplateOpen] = useState(false)

  const filteredInadimplentes = inadimplentes.filter(inadimplente => {
    const matchesSearch = inadimplente.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         inadimplente.email?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "TODOS" || inadimplente.status_envio === statusFilter
    return matchesSearch && matchesStatus
  })

  const totalInadimplencia = inadimplentes.reduce((sum, item) => sum + item.valor, 0)
  const pendentesEnvio = inadimplentes.filter(i => i.status_envio === "PENDENTE").length

  const handleSelectAll = () => {
    if (selectedInadimplentes.length === filteredInadimplentes.length) {
      setSelectedInadimplentes([])
    } else {
      setSelectedInadimplentes(filteredInadimplentes.map(i => i.id))
    }
  }

  const handleSelectInadimplente = (id: string) => {
    setSelectedInadimplentes(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id)
        : [...prev, id]
    )
  }

  const handleSendCobranca = (tipo: 'email' | 'whatsapp' | 'sms') => {
    console.log(`Enviando cobrança por ${tipo} para:`, selectedInadimplentes)
    // Aqui seria implementado o envio real
    setSelectedInadimplentes([])
  }

  return (
    <ProtectedRoute requiredPermission="FINANCEIRO">
      <LayoutProvider>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Cobrança</h1>
              <p className="text-muted-foreground">
                Gerencie cobranças e notificações para sócios inadimplentes
              </p>
            </div>
            <div className="flex gap-2">
              <Dialog open={isTemplateOpen} onOpenChange={setIsTemplateOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <FileText className="h-4 w-4 mr-2" />
                    Templates
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-4xl">
                  <DialogHeader>
                    <DialogTitle>Templates de Cobrança</DialogTitle>
                    <DialogDescription>
                      Gerencie os templates de mensagem para cobrança
                    </DialogDescription>
                  </DialogHeader>
                  <TemplateCobranca onSuccess={() => setIsTemplateOpen(false)} />
                </DialogContent>
              </Dialog>
              
              <Button 
                disabled={selectedInadimplentes.length === 0}
                onClick={() => setIsCobrancaOpen(true)}
              >
                <Send className="h-4 w-4 mr-2" />
                Enviar Cobrança
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Total Inadimplência
                    </p>
                    <p className="text-2xl font-bold">R$ {totalInadimplencia.toFixed(2)}</p>
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
                      Inadimplentes
                    </p>
                    <p className="text-2xl font-bold">{inadimplentes.length}</p>
                  </div>
                  <Users className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Pendentes de Envio
                    </p>
                    <p className="text-2xl font-bold">{pendentesEnvio}</p>
                  </div>
                  <Clock className="h-8 w-8 text-yellow-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Taxa de Resposta
                    </p>
                    <p className="text-2xl font-bold">68%</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Dialog de Envio de Cobrança */}
          <Dialog open={isCobrancaOpen} onOpenChange={setIsCobrancaOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Enviar Cobrança</DialogTitle>
                <DialogDescription>
                  Selecione o método de envio para {selectedInadimplentes.length} sócios
                </DialogDescription>
              </DialogHeader>
              <CobrancaForm 
                selectedCount={selectedInadimplentes.length}
                onSend={(tipo) => {
                  handleSendCobranca(tipo)
                  setIsCobrancaOpen(false)
                }}
                onCancel={() => setIsCobrancaOpen(false)}
              />
            </DialogContent>
          </Dialog>

          <Tabs defaultValue="inadimplentes" className="space-y-4">
            <TabsList>
              <TabsTrigger value="inadimplentes">Inadimplentes</TabsTrigger>
              <TabsTrigger value="historico">Histórico</TabsTrigger>
              <TabsTrigger value="automacao">Automação</TabsTrigger>
            </TabsList>

            <TabsContent value="inadimplentes">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Lista de Inadimplentes</CardTitle>
                    <div className="flex gap-2">
                      <Button 
                        variant="outline"
                        size="sm"
                        disabled={selectedInadimplentes.length === 0}
                        onClick={() => handleSendCobranca('email')}
                      >
                        <Mail className="h-4 w-4 mr-2" />
                        Email
                      </Button>
                      <Button 
                        variant="outline"
                        size="sm"
                        disabled={selectedInadimplentes.length === 0}
                        onClick={() => handleSendCobranca('whatsapp')}
                      >
                        <MessageSquare className="h-4 w-4 mr-2" />
                        WhatsApp
                      </Button>
                      <Button 
                        variant="outline"
                        size="sm"
                        disabled={selectedInadimplentes.length === 0}
                        onClick={() => handleSendCobranca('sms')}
                      >
                        <Phone className="h-4 w-4 mr-2" />
                        SMS
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Exportar
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2 mb-4">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        placeholder="Buscar inadimplentes..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                      <SelectTrigger className="w-[150px]">
                        <Filter className="h-4 w-4 mr-2" />
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="TODOS">Todos</SelectItem>
                        <SelectItem value="ENVIADO">Enviado</SelectItem>
                        <SelectItem value="PENDENTE">Pendente</SelectItem>
                        <SelectItem value="FALHOU">Falhou</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-2 p-2 border-b">
                      <input
                        type="checkbox"
                        checked={selectedInadimplentes.length === filteredInadimplentes.length}
                        onChange={handleSelectAll}
                        className="rounded"
                      />
                      <span className="text-sm font-medium">
                        {selectedInadimplentes.length} de {filteredInadimplentes.length} selecionados
                      </span>
                    </div>
                    
                    {filteredInadimplentes.map((inadimplente) => (
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
                            <Badge className={getStatusColor(inadimplente.status_envio)}>
                              {inadimplente.status_envio}
                            </Badge>
                            {inadimplente.ultimo_contato && (
                              <span className="text-xs text-muted-foreground">
                                Último contato: {new Date(inadimplente.ultimo_contato).toLocaleDateString('pt-BR')}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="historico">
              <Card>
                <CardHeader>
                  <CardTitle>Histórico de Cobranças</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Sócio</TableHead>
                          <TableHead>Tipo</TableHead>
                          <TableHead>Mensagem</TableHead>
                          <TableHead>Data Envio</TableHead>
                          <TableHead>Status</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {historicoCobranca.map((cobranca) => (
                          <TableRow key={cobranca.id}>
                            <TableCell className="font-medium">
                              {cobranca.socio_nome}
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                {getTipoIcon(cobranca.tipo)}
                                <span>{cobranca.tipo}</span>
                              </div>
                            </TableCell>
                            <TableCell className="max-w-xs truncate">
                              {cobranca.mensagem}
                            </TableCell>
                            <TableCell>
                              {new Date(cobranca.data_envio).toLocaleString('pt-BR')}
                            </TableCell>
                            <TableCell>
                              <Badge className={getStatusColor(cobranca.status)}>
                                {cobranca.status}
                              </Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="automacao">
              <Card>
                <CardHeader>
                  <CardTitle>Automação de Cobrança</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="p-4 border rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Bell className="h-5 w-5 text-blue-600" />
                          <h3 className="font-semibold">Lembrete Automático</h3>
                        </div>
                        <p className="text-sm text-muted-foreground mb-4">
                          Envia lembrete 3 dias antes do vencimento
                        </p>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                          <span className="text-sm text-green-600">Ativo</span>
                        </div>
                      </div>

                      <div className="p-4 border rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertTriangle className="h-5 w-5 text-orange-600" />
                          <h3 className="font-semibold">Cobrança Automática</h3>
                        </div>
                        <p className="text-sm text-muted-foreground mb-4">
                          Envia cobrança após 5 dias de atraso
                        </p>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                          <span className="text-sm text-green-600">Ativo</span>
                        </div>
                      </div>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="p-4 border rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Mail className="h-5 w-5 text-purple-600" />
                          <h3 className="font-semibold">Notificação por Email</h3>
                        </div>
                        <p className="text-sm text-muted-foreground mb-4">
                          Envia notificações por email padrão
                        </p>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                          <span className="text-sm text-green-600">Ativo</span>
                        </div>
                      </div>

                      <div className="p-4 border rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <MessageSquare className="h-5 w-5 text-green-600" />
                          <h3 className="font-semibold">Notificação por WhatsApp</h3>
                        </div>
                        <p className="text-sm text-muted-foreground mb-4">
                          Envia notificações por WhatsApp para números cadastrados
                        </p>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-yellow-600 rounded-full"></div>
                          <span className="text-sm text-yellow-600">Configurar</span>
                        </div>
                      </div>
                    </div>
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