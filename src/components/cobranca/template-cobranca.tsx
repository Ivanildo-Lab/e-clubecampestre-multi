"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
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
  Plus,
  Edit,
  Trash2,
  Mail,
  MessageSquare,
  Phone,
  FileText,
  Save,
  Eye
} from "lucide-react"

interface TemplateCobrancaProps {
  onSuccess: () => void
}

// Templates mockados
const templates = [
  {
    id: "1",
    nome: "Lembrete de Pagamento",
    tipo: "EMAIL",
    assunto: "Lembrete de pagamento - Clube Campestre",
    mensagem: `Prezado(a) Sócio(a),

Identificamos que sua mensalidade está em atraso. Por favor, regularize sua situação o mais breve possível.

Valor em atraso: R$ {valor}
Dias de atraso: {dias_atraso}

Para realizar o pagamento, você pode utilizar uma das seguintes opções:
• PIX: chave pix@clubemanager.com
• Boleto bancário: disponível no sistema
• Presencialmente na secretaria

Caso já tenha realizado o pagamento, por favor, desconsidere esta mensagem.

Atenciosamente,
Equipe do Clube Campestre`,
    ativo: true,
  },
  {
    id: "2",
    nome: "Cobrança WhatsApp",
    tipo: "WHATSAPP",
    assunto: "",
    mensagem: `Olá, {nome}! 😊

Identificamos que sua mensalidade do Clube Campestre está em atraso há {dias_atraso} dias.

Valor devido: R$ {valor}

Para regularizar, você pode:
• Pagar via PIX: pix@clubemanager.com
• Gerar boleto no sistema
• Pagar presencialmente

Precisa de ajuda? Responda esta mensagem! 📞`,
    ativo: true,
  },
  {
    id: "3",
    nome: "Notificação SMS",
    tipo: "SMS",
    assunto: "",
    mensagem: `Clube Campestre: Olá {nome}, sua mensalidade de R$ {valor} está atrasada há {dias_atraso} dias. Regularize via PIX: pix@clubemanager.com ou ligue (11) 9999-0000.`,
    ativo: false,
  },
]

export function TemplateCobranca({ onSuccess }: TemplateCobrancaProps) {
  const [selectedTemplate, setSelectedTemplate] = useState(templates[0])
  const [isEditing, setIsEditing] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [editForm, setEditForm] = useState({
    nome: "",
    tipo: "EMAIL",
    assunto: "",
    mensagem: "",
    ativo: true,
  })

  const handleEdit = (template: any) => {
    setEditForm({
      nome: template.nome,
      tipo: template.tipo,
      assunto: template.assunto,
      mensagem: template.mensagem,
      ativo: template.ativo,
    })
    setIsEditing(true)
  }

  const handleSave = () => {
    console.log("Salvando template:", editForm)
    setIsEditing(false)
    setIsCreating(false)
  }

  const handleCreate = () => {
    setEditForm({
      nome: "",
      tipo: "EMAIL",
      assunto: "",
      mensagem: "",
      ativo: true,
    })
    setIsCreating(true)
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
        return <FileText className="h-4 w-4" />
    }
  }

  const getTipoColor = (tipo: string) => {
    switch (tipo) {
      case "EMAIL":
        return "bg-blue-100 text-blue-800"
      case "WHATSAPP":
        return "bg-green-100 text-green-800"
      case "SMS":
        return "bg-purple-100 text-purple-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Templates de Cobrança</h3>
        <Button onClick={handleCreate}>
          <Plus className="h-4 w-4 mr-2" />
          Novo Template
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Lista de Templates */}
        <Card>
          <CardHeader>
            <CardTitle>Templates Disponíveis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedTemplate.id === template.id
                      ? 'ring-2 ring-blue-500 bg-blue-50'
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedTemplate(template)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getTipoIcon(template.tipo)}
                      <div>
                        <div className="font-medium">{template.nome}</div>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge className={getTipoColor(template.tipo)}>
                            {template.tipo}
                          </Badge>
                          {template.ativo && (
                            <Badge className="bg-green-100 text-green-800">
                              Ativo
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleEdit(template)
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Preview do Template */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Preview
              <Button variant="outline" size="sm">
                <Eye className="h-4 w-4 mr-2" />
                Testar
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label className="text-sm font-medium">Nome</Label>
                <p className="text-sm text-muted-foreground">{selectedTemplate.nome}</p>
              </div>
              
              <div>
                <Label className="text-sm font-medium">Tipo</Label>
                <div className="flex items-center gap-2 mt-1">
                  {getTipoIcon(selectedTemplate.tipo)}
                  <Badge className={getTipoColor(selectedTemplate.tipo)}>
                    {selectedTemplate.tipo}
                  </Badge>
                </div>
              </div>

              {selectedTemplate.assunto && (
                <div>
                  <Label className="text-sm font-medium">Assunto</Label>
                  <p className="text-sm text-muted-foreground">{selectedTemplate.assunto}</p>
                </div>
              )}

              <div>
                <Label className="text-sm font-medium">Mensagem</Label>
                <div className="mt-1 p-3 bg-gray-50 rounded-md text-sm whitespace-pre-wrap">
                  {selectedTemplate.mensagem}
                </div>
              </div>

              <div className="text-xs text-muted-foreground">
                <p>Variáveis disponíveis:</p>
                <p>{'{nome}, {valor}, {dias_atraso}, {data_vencimento}, {categoria}'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Dialog de Edição/Criação */}
      <Dialog open={isEditing || isCreating} onOpenChange={() => {
        setIsEditing(false)
        setIsCreating(false)
      }}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {isEditing ? "Editar Template" : "Novo Template"}
            </DialogTitle>
            <DialogDescription>
              {isEditing ? "Altere as informações do template" : "Preencha os dados para criar um novo template"}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="nome">Nome do Template *</Label>
                <Input
                  id="nome"
                  value={editForm.nome}
                  onChange={(e) => setEditForm({ ...editForm, nome: e.target.value })}
                  placeholder="Ex: Lembrete de Pagamento"
                />
              </div>
              
              <div>
                <Label htmlFor="tipo">Tipo *</Label>
                <Select value={editForm.tipo} onValueChange={(value) => setEditForm({ ...editForm, tipo: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EMAIL">Email</SelectItem>
                    <SelectItem value="WHATSAPP">WhatsApp</SelectItem>
                    <SelectItem value="SMS">SMS</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {editForm.tipo === "EMAIL" && (
              <div>
                <Label htmlFor="assunto">Assunto</Label>
                <Input
                  id="assunto"
                  value={editForm.assunto}
                  onChange={(e) => setEditForm({ ...editForm, assunto: e.target.value })}
                  placeholder="Assunto do email"
                />
              </div>
            )}

            <div>
              <Label htmlFor="mensagem">Mensagem *</Label>
              <Textarea
                id="mensagem"
                value={editForm.mensagem}
                onChange={(e) => setEditForm({ ...editForm, mensagem: e.target.value })}
                placeholder="Digite a mensagem..."
                rows={8}
              />
            </div>

            <div className="text-xs text-muted-foreground">
              <p>Variáveis disponíveis:</p>
              <p>{'{nome}, {valor}, {dias_atraso}, {data_vencimento}, {categoria}'}</p>
            </div>

            <div className="flex justify-end gap-4">
              <Button variant="outline" onClick={() => {
                setIsEditing(false)
                setIsCreating(false)
              }}>
                Cancelar
              </Button>
              <Button onClick={handleSave}>
                <Save className="h-4 w-4 mr-2" />
                Salvar
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}