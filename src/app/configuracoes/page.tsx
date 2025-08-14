"use client"

import { useState } from "react"
import { LayoutProvider } from "@/components/layout/layout-provider"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
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
  Settings,
  Users,
  CreditCard,
  Bell,
  Mail,
  MessageSquare,
  Phone,
  Save,
  RefreshCw
} from "lucide-react"

export default function ConfiguracoesPage() {
  const [isLoading, setIsLoading] = useState(false)

  const handleSave = async () => {
    setIsLoading(true)
    try {
      // Simulação de salvamento - depois será substituído pela API real
      await new Promise(resolve => setTimeout(resolve, 1000))
      console.log("Configurações salvas")
    } catch (error) {
      console.error("Erro ao salvar configurações:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <ProtectedRoute requiredPermission="ADMINISTRADOR">
      <LayoutProvider>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Configurações</h1>
              <p className="text-muted-foreground">
                Gerencie as configurações do sistema
              </p>
            </div>
            <Button onClick={handleSave} disabled={isLoading}>
              <Save className="h-4 w-4 mr-2" />
              {isLoading ? "Salvando..." : "Salvar Alterações"}
            </Button>
          </div>

          <Tabs defaultValue="geral" className="space-y-4">
            <TabsList>
              <TabsTrigger value="geral">Geral</TabsTrigger>
              <TabsTrigger value="mensalidades">Mensalidades</TabsTrigger>
              <TabsTrigger value="notificacoes">Notificações</TabsTrigger>
              <TabsTrigger value="usuarios">Usuários</TabsTrigger>
            </TabsList>

            <TabsContent value="geral">
              <div className="grid gap-6 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="h-5 w-5" />
                      Informações do Clube
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="nome_clube">Nome do Clube</Label>
                      <Input id="nome_clube" defaultValue="Clube Campestre" />
                    </div>
                    <div>
                      <Label htmlFor="cnpj">CNPJ</Label>
                      <Input id="cnpj" defaultValue="00.000.000/0001-00" />
                    </div>
                    <div>
                      <Label htmlFor="endereco">Endereço</Label>
                      <Input id="endereco" defaultValue="Rua das Flores, 123 - São Paulo, SP" />
                    </div>
                    <div>
                      <Label htmlFor="telefone">Telefone</Label>
                      <Input id="telefone" defaultValue="(11) 9999-0000" />
                    </div>
                    <div>
                      <Label htmlFor="email">Email</Label>
                      <Input id="email" defaultValue="contato@clubemanager.com" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Configurações do Sistema</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Modo de Manutenção</Label>
                        <p className="text-sm text-muted-foreground">
                          Colocar o sistema em modo de manutenção
                        </p>
                      </div>
                      <Switch />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Backup Automático</Label>
                        <p className="text-sm text-muted-foreground">
                          Realizar backup automático diariamente
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Notificações por Email</Label>
                        <p className="text-sm text-muted-foreground">
                          Enviar notificações por email
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div>
                      <Label htmlFor="timezone">Fuso Horário</Label>
                      <Select defaultValue="America/Sao_Paulo">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="America/Sao_Paulo">
                            America/Sao_Paulo (GMT-3)
                          </SelectItem>
                          <SelectItem value="America/Manaus">
                            America/Manaus (GMT-4)
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="mensalidades">
              <div className="grid gap-6 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CreditCard className="h-5 w-5" />
                      Valores das Mensalidades
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="valor_titular">Valor Titular (R$)</Label>
                      <Input id="valor_titular" type="number" step="0.01" defaultValue="150.00" />
                    </div>
                    <div>
                      <Label htmlFor="valor_dependente">Valor Dependente (R$)</Label>
                      <Input id="valor_dependente" type="number" step="0.01" defaultValue="100.00" />
                    </div>
                    <div>
                      <Label htmlFor="valor_contribuinte">Valor Contribuinte (R$)</Label>
                      <Input id="valor_contribuinte" type="number" step="0.01" defaultValue="75.00" />
                    </div>
                    <div>
                      <Label htmlFor="valor_benemerito">Valor Benemérito (R$)</Label>
                      <Input id="valor_benemerito" type="number" step="0.01" defaultValue="200.00" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Configurações de Vencimento</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="dia_vencimento">Dia de Vencimento Padrão</Label>
                      <Input id="dia_vencimento" type="number" min="1" max="31" defaultValue="5" />
                    </div>
                    <div>
                      <Label htmlFor="gerar_automatico">Gerar Mensalidades Automaticamente</Label>
                      <Select defaultValue="1">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">Dia 1 de cada mês</SelectItem>
                          <SelectItem value="5">Dia 5 de cada mês</SelectItem>
                          <SelectItem value="10">Dia 10 de cada mês</SelectItem>
                          <SelectItem value="0">Não gerar automaticamente</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="juros_atraso">Juros por Atraso (%)</Label>
                      <Input id="juros_atraso" type="number" step="0.1" defaultValue="2.0" />
                    </div>
                    <div>
                      <Label htmlFor="multa_atraso">Multa por Atraso (R$)</Label>
                      <Input id="multa_atraso" type="number" step="0.01" defaultValue="10.00" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="notificacoes">
              <div className="grid gap-6 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Bell className="h-5 w-5" />
                      Configurações de Notificação
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Lembrete de Vencimento</Label>
                        <p className="text-sm text-muted-foreground">
                          Enviar lembrete 3 dias antes do vencimento
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Notificação de Atraso</Label>
                        <p className="text-sm text-muted-foreground">
                          Enviar notificação após 5 dias de atraso
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Confirmação de Pagamento</Label>
                        <p className="text-sm text-muted-foreground">
                          Enviar confirmação quando pagamento for registrado
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div>
                      <Label htmlFor="email_remetente">Email Remetente</Label>
                      <Input id="email_remetente" defaultValue="noreply@clubemanager.com" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Integrações</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="whatsapp_api">API WhatsApp</Label>
                      <Input id="whatsapp_api" placeholder="URL da API do WhatsApp" />
                    </div>
                    <div>
                      <Label htmlFor="sms_api">API SMS</Label>
                      <Input id="sms_api" placeholder="URL da API de SMS" />
                    </div>
                    <div>
                      <Label htmlFor="email_smtp">Servidor SMTP</Label>
                      <Input id="email_smtp" placeholder="smtp.gmail.com:587" />
                    </div>
                    <div>
                      <Label htmlFor="email_usuario">Usuário Email</Label>
                      <Input id="email_usuario" placeholder="seuemail@gmail.com" />
                    </div>
                    <div>
                      <Label htmlFor="email_senha">Senha Email</Label>
                      <Input id="email_senha" type="password" placeholder="Sua senha" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="usuarios">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Gerenciamento de Usuários
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="text-center py-8 text-muted-foreground">
                      <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Funcionalidade de gerenciamento de usuários em desenvolvimento.</p>
                      <p className="text-sm">Aqui você poderá cadastrar, editar e remover usuários do sistema.</p>
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