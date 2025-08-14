"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Phone, 
  Mail, 
  MapPin, 
  Calendar, 
  Users,
  CreditCard,
  FileText,
  MessageSquare,
  Edit,
  Plus
} from "lucide-react"

interface SocioDetailsProps {
  socio: any
}

export function SocioDetails({ socio }: SocioDetailsProps) {
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

  // Dados mockados para demonstração
  const mensalidades = [
    { id: "1", mes: "Janeiro/2024", valor: 150.00, status: "PAGO", data_pagamento: "2024-01-05" },
    { id: "2", mes: "Fevereiro/2024", valor: 150.00, status: "PAGO", data_pagamento: "2024-02-03" },
    { id: "3", mes: "Março/2024", valor: 150.00, status: "PENDENTE", data_pagamento: null },
  ]

  const interacoes = [
    { id: "1", tipo: "COMUNICACAO", descricao: "Email enviado sobre evento de churrasco", data: "2024-03-01" },
    { id: "2", tipo: "REUNIAO", descricao: "Participou da reunião de planejamento", data: "2024-02-15" },
    { id: "3", tipo: "ANOTACAO", descricao: "Solicitou informações sobre novas categorias", data: "2024-02-10" },
  ]

  const dependentes = [
    { id: "1", nome: "Carlos Silva", relacionamento: "Filho", data_nascimento: "2010-05-15" },
    { id: "2", nome: "Ana Silva", relacionamento: "Esposa", data_nascimento: "1985-08-20" },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <Avatar className="h-16 w-16">
            <AvatarFallback className="text-lg">
              {socio.nome.split(' ').map(n => n[0]).join('')}
            </AvatarFallback>
          </Avatar>
          <div>
            <h2 className="text-2xl font-bold">{socio.nome}</h2>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={getCategoriaColor(socio.categoria)}>
                {socio.categoria}
              </Badge>
              <Badge className={getStatusColor(socio.status)}>
                {socio.status}
              </Badge>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Edit className="h-4 w-4 mr-2" />
            Editar
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Nova Interação
          </Button>
        </div>
      </div>

      {/* Informações Básicas */}
      <Card>
        <CardHeader>
          <CardTitle>Informações Básicas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">
                  <strong>Adesão:</strong> {new Date(socio.data_adesao).toLocaleDateString('pt-BR')}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">
                  <strong>Telefone:</strong> {socio.telefone || "Não informado"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">
                  <strong>Email:</strong> {socio.email || "Não informado"}
                </span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">
                  <strong>Endereço:</strong> {socio.endereco || "Não informado"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">
                  <strong>Dependentes:</strong> {socio.dependentes}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <CreditCard className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">
                  <strong>CPF:</strong> {socio.cpf}
                </span>
              </div>
            </div>
          </div>
          {socio.anotacoes && (
            <>
              <Separator className="my-4" />
              <div>
                <h4 className="font-medium mb-2">Anotações Internas</h4>
                <p className="text-sm text-muted-foreground">{socio.anotacoes}</p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="mensalidades" className="space-y-4">
        <TabsList>
          <TabsTrigger value="mensalidades">Mensalidades</TabsTrigger>
          <TabsTrigger value="interacoes">Interações</TabsTrigger>
          <TabsTrigger value="dependentes">Dependentes</TabsTrigger>
        </TabsList>

        <TabsContent value="mensalidades">
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Mensalidades</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mensalidades.map((mensalidade) => (
                  <div key={mensalidade.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <div className="font-medium">{mensalidade.mes}</div>
                      <div className="text-sm text-muted-foreground">
                        Valor: R$ {mensalidade.valor.toFixed(2)}
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge 
                        className={
                          mensalidade.status === "PAGO" 
                            ? "bg-green-100 text-green-800" 
                            : "bg-yellow-100 text-yellow-800"
                        }
                      >
                        {mensalidade.status}
                      </Badge>
                      {mensalidade.data_pagamento && (
                        <div className="text-xs text-muted-foreground mt-1">
                          Pago em {new Date(mensalidade.data_pagamento).toLocaleDateString('pt-BR')}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="interacoes">
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Interações</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {interacoes.map((interacao) => (
                  <div key={interacao.id} className="flex items-start gap-3 p-3 border rounded-lg">
                    <div className="p-2 rounded-full bg-muted">
                      <MessageSquare className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div className="font-medium">{interacao.tipo}</div>
                        <div className="text-xs text-muted-foreground">
                          {new Date(interacao.data).toLocaleDateString('pt-BR')}
                        </div>
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">
                        {interacao.descricao}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dependentes">
          <Card>
            <CardHeader>
              <CardTitle>Dependentes</CardTitle>
            </CardHeader>
            <CardContent>
              {dependentes.length > 0 ? (
                <div className="space-y-3">
                  {dependentes.map((dependente) => (
                    <div key={dependente.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback>
                            {dependente.nome.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">{dependente.nome}</div>
                          <div className="text-sm text-muted-foreground">
                            {dependente.relacionamento} • Nascido em {new Date(dependente.data_nascimento).toLocaleDateString('pt-BR')}
                          </div>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        Ver Detalhes
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Este sócio não possui dependentes cadastrados.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}