"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Mail, MessageSquare, Phone, Send } from "lucide-react"

interface CobrancaFormProps {
  selectedCount: number
  onSend: (tipo: 'email' | 'whatsapp' | 'sms') => void
  onCancel: () => void
}

export function CobrancaForm({ selectedCount, onSend, onCancel }: CobrancaFormProps) {
  const [selectedMethod, setSelectedMethod] = useState<'email' | 'whatsapp' | 'sms'>('email')

  const methods = [
    {
      id: 'email' as const,
      title: 'Email',
      description: 'Envia notificação por email com template personalizado',
      icon: Mail,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      id: 'whatsapp' as const,
      title: 'WhatsApp',
      description: 'Envia mensagem direta no WhatsApp',
      icon: MessageSquare,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      id: 'sms' as const,
      title: 'SMS',
      description: 'Envia mensagem de texto por SMS',
      icon: Phone,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Resumo */}
      <Card>
        <CardHeader>
          <CardTitle>Resumo do Envio</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total de destinatários</p>
              <p className="text-2xl font-bold">{selectedCount} sócios</p>
            </div>
            <Badge variant="outline" className="text-lg px-3 py-1">
              {selectedCount} selecionados
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Métodos de Envio */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Selecione o método de envio</h3>
        <div className="grid gap-4 md:grid-cols-3">
          {methods.map((method) => (
            <Card
              key={method.id}
              className={`cursor-pointer transition-colors ${
                selectedMethod === method.id
                  ? 'ring-2 ring-blue-500 bg-blue-50'
                  : 'hover:bg-gray-50'
              }`}
              onClick={() => setSelectedMethod(method.id)}
            >
              <CardContent className="p-4">
                <div className="flex flex-col items-center text-center">
                  <div className={`p-3 rounded-full ${method.bgColor} mb-3`}>
                    <method.icon className={`h-6 w-6 ${method.color}`} />
                  </div>
                  <h4 className="font-semibold mb-2">{method.title}</h4>
                  <p className="text-sm text-muted-foreground">
                    {method.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Preview da Mensagem */}
      <Card>
        <CardHeader>
          <CardTitle>Preview da Mensagem</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm">
                <strong>Assunto:</strong> Lembrete de pagamento - Clube Campestre
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm whitespace-pre-wrap">
Prezado(a) Sócio(a),

Identificamos que sua mensalidade está em atraso. Por favor, regularize sua situação o mais breve possível.

Valor em atraso: R$ 150,00
Dias de atraso: 15 dias

Para realizar o pagamento, você pode utilizar uma das seguintes opções:
• PIX: chave pix@clubemanager.com
• Boleto bancário: disponível no sistema
• Presencialmente na secretaria

Caso já tenha realizado o pagamento, por favor, desconsidere esta mensagem.

Atenciosamente,
Equipe do Clube Campestre
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button onClick={() => onSend(selectedMethod)}>
          <Send className="h-4 w-4 mr-2" />
          Enviar {methods.find(m => m.id === selectedMethod)?.title}
        </Button>
      </div>
    </div>
  )
}