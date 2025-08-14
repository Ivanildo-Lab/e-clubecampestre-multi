"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Calendar, Users, AlertCircle } from "lucide-react"

const gerarMensalidadesSchema = z.object({
  mes: z.string().min(1, "Selecione o mês"),
  ano: z.string().min(1, "Selecione o ano"),
  dia_vencimento: z.number().min(1).max(31, "Dia deve estar entre 1 e 31"),
  valor_titular: z.number().min(0.01, "Valor deve ser maior que zero"),
  valor_dependente: z.number().min(0.01, "Valor deve ser maior que zero"),
  gerar_para: z.enum(["TODOS", "ATIVOS", "TITULARES"]),
})

type GerarMensalidadesFormData = z.infer<typeof gerarMensalidadesSchema>

interface GerarMensalidadesProps {
  onSuccess: () => void
}

export function GerarMensalidades({ onSuccess }: GerarMensalidadesProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [preview, setPreview] = useState<any[]>([])

  const form = useForm<GerarMensalidadesFormData>({
    resolver: zodResolver(gerarMensalidadesSchema),
    defaultValues: {
      mes: new Date().getMonth() + 1,
      ano: new Date().getFullYear(),
      dia_vencimento: 5,
      valor_titular: 150.00,
      valor_dependente: 100.00,
      gerar_para: "ATIVOS",
    },
  })

  const calcularPreview = () => {
    const values = form.getValues()
    
    // Simulação de preview - depois será substituído pela API real
    const mockPreview = [
      { nome: "João Silva", categoria: "TITULAR", valor: values.valor_titular },
      { nome: "Maria Santos", categoria: "TITULAR", valor: values.valor_titular },
      { nome: "Pedro Oliveira", categoria: "DEPENDENTE", valor: values.valor_dependente },
      { nome: "Ana Costa", categoria: "TITULAR", valor: values.valor_titular },
    ].filter(socio => {
      if (values.gerar_para === "TODOS") return true
      if (values.gerar_para === "ATIVOS") return true // Simulação
      if (values.gerar_para === "TITULARES") return socio.categoria === "TITULAR"
      return true
    })

    setPreview(mockPreview)
  }

  const onSubmit = async (data: GerarMensalidadesFormData) => {
    setIsLoading(true)
    try {
      // Simulação de geração - depois será substituído pela API real
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      console.log("Gerando mensalidades:", data)
      onSuccess()
    } catch (error) {
      console.error("Erro ao gerar mensalidades:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Período */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Período
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="mes"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Mês *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Mês" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="1">Janeiro</SelectItem>
                          <SelectItem value="2">Fevereiro</SelectItem>
                          <SelectItem value="3">Março</SelectItem>
                          <SelectItem value="4">Abril</SelectItem>
                          <SelectItem value="5">Maio</SelectItem>
                          <SelectItem value="6">Junho</SelectItem>
                          <SelectItem value="7">Julho</SelectItem>
                          <SelectItem value="8">Agosto</SelectItem>
                          <SelectItem value="9">Setembro</SelectItem>
                          <SelectItem value="10">Outubro</SelectItem>
                          <SelectItem value="11">Novembro</SelectItem>
                          <SelectItem value="12">Dezembro</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="ano"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Ano *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Ano" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="2024">2024</SelectItem>
                          <SelectItem value="2025">2025</SelectItem>
                          <SelectItem value="2026">2026</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="dia_vencimento"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Dia de Vencimento *</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="1"
                        max="31"
                        placeholder="5"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Valores */}
          <Card>
            <CardHeader>
              <CardTitle>Valores</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="valor_titular"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Valor Titular *</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="150,00"
                        {...field}
                        onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="valor_dependente"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Valor Dependente *</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="100,00"
                        {...field}
                        onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="gerar_para"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Gerar Para</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="TODOS">Todos os Sócios</SelectItem>
                        <SelectItem value="ATIVOS">Apenas Sócios Ativos</SelectItem>
                        <SelectItem value="TITULARES">Apenas Titulares</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        </div>

        {/* Preview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Preview ({preview.length} sócios)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {preview.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Clique em "Calcular Preview" para ver a lista de sócios</p>
                </div>
              ) : (
                preview.map((socio, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <div className="font-medium">{socio.nome}</div>
                      <div className="text-sm text-muted-foreground">{socio.categoria}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">R$ {socio.valor.toFixed(2)}</div>
                    </div>
                  </div>
                ))
              )}
            </div>
            
            <div className="flex justify-between items-center mt-4 pt-4 border-t">
              <Button 
                type="button" 
                variant="outline" 
                onClick={calcularPreview}
              >
                Calcular Preview
              </Button>
              
              {preview.length > 0 && (
                <div className="text-right">
                  <div className="text-sm text-muted-foreground">Total Previsto</div>
                  <div className="text-lg font-bold">
                    R$ {preview.reduce((sum, s) => sum + s.valor, 0).toFixed(2)}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Button type="button" variant="outline" onClick={onSuccess}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading || preview.length === 0}>
            {isLoading ? "Gerando..." : `Gerar ${preview.length} Mensalidades`}
          </Button>
        </div>
      </form>
    </Form>
  )
}