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

const mensalidadeSchema = z.object({
  id_socio: z.string().min(1, "Selecione um sócio"),
  valor: z.number().min(0.01, "Valor deve ser maior que zero"),
  data_vencimento: z.string().min(1, "Data de vencimento é obrigatória"),
  status: z.enum(["PENDENTE", "PAGO", "ATRASADO", "CANCELADO"]),
  data_pagamento: z.string().optional(),
  forma_pagamento: z.string().optional(),
  juros: z.number().min(0).default(0),
  multa: z.number().min(0).default(0),
})

type MensalidadeFormData = z.infer<typeof mensalidadeSchema>

interface MensalidadeFormProps {
  mensalidade?: any
  onSuccess: () => void
}

export function MensalidadeForm({ mensalidade, onSuccess }: MensalidadeFormProps) {
  const [isLoading, setIsLoading] = useState(false)

  const form = useForm<MensalidadeFormData>({
    resolver: zodResolver(mensalidadeSchema),
    defaultValues: {
      id_socio: mensalidade?.id_socio || "",
      valor: mensalidade?.valor || 0,
      data_vencimento: mensalidade?.data_vencimento || "",
      status: mensalidade?.status || "PENDENTE",
      data_pagamento: mensalidade?.data_pagamento || "",
      forma_pagamento: mensalidade?.forma_pagamento || "",
      juros: mensalidade?.juros || 0,
      multa: mensalidade?.multa || 0,
    },
  })

  const status = form.watch("status")

  const onSubmit = async (data: MensalidadeFormData) => {
    setIsLoading(true)
    try {
      // Simulação de salvamento - depois será substituído pela API real
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      console.log("Salvando mensalidade:", data)
      onSuccess()
    } catch (error) {
      console.error("Erro ao salvar mensalidade:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Dados da Mensalidade */}
          <Card>
            <CardHeader>
              <CardTitle>Dados da Mensalidade</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="id_socio"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Sócio *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o sócio" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="1">João Silva</SelectItem>
                        <SelectItem value="2">Maria Santos</SelectItem>
                        <SelectItem value="3">Pedro Oliveira</SelectItem>
                        <SelectItem value="4">Ana Costa</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="valor"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Valor *</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="0,00"
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
                name="data_vencimento"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Data de Vencimento *</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o status" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="PENDENTE">Pendente</SelectItem>
                        <SelectItem value="PAGO">Pago</SelectItem>
                        <SelectItem value="ATRASADO">Atrasado</SelectItem>
                        <SelectItem value="CANCELADO">Cancelado</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Dados do Pagamento */}
          <Card>
            <CardHeader>
              <CardTitle>Dados do Pagamento</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {status === "PAGO" && (
                <>
                  <FormField
                    control={form.control}
                    name="data_pagamento"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Data do Pagamento</FormLabel>
                        <FormControl>
                          <Input type="date" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="forma_pagamento"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Forma de Pagamento</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione a forma" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="PIX">PIX</SelectItem>
                            <SelectItem value="BOLETO">Boleto Bancário</SelectItem>
                            <SelectItem value="TRANSFERENCIA">Transferência</SelectItem>
                            <SelectItem value="DINHEIRO">Dinheiro</SelectItem>
                            <SelectItem value="CARTAO">Cartão</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              )}

              {status === "ATRASADO" && (
                <>
                  <FormField
                    control={form.control}
                    name="juros"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Juros</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="0.01"
                            placeholder="0,00"
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
                    name="multa"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Multa</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="0.01"
                            placeholder="0,00"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Button type="button" variant="outline" onClick={onSuccess}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Salvando..." : mensalidade ? "Atualizar" : "Cadastrar"}
          </Button>
        </div>
      </form>
    </Form>
  )
}