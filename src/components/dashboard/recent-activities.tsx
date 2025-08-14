"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  UserPlus, 
  CreditCard, 
  Calendar, 
  MessageSquare,
  Clock
} from "lucide-react"

const activities = [
  {
    id: 1,
    type: "novo_socio",
    title: "Novo sócio cadastrado",
    description: "Maria Santos foi cadastrada como sócia titular",
    time: "há 5 minutos",
    icon: UserPlus,
    iconColor: "text-green-600",
  },
  {
    id: 2,
    type: "pagamento",
    title: "Pagamento recebido",
    description: "João Silva pagou mensalidade de R$ 150,00",
    time: "há 1 hora",
    icon: CreditCard,
    iconColor: "text-blue-600",
  },
  {
    id: 3,
    type: "evento",
    title: "Novo evento criado",
    description: "Churrasco de fim de semana agendado",
    time: "há 2 horas",
    icon: Calendar,
    iconColor: "text-purple-600",
  },
  {
    id: 4,
    type: "comunicacao",
    title: "Comunicação enviada",
    description: "Email enviado para todos os sócios",
    time: "há 3 horas",
    icon: MessageSquare,
    iconColor: "text-orange-600",
  },
  {
    id: 5,
    type: "lembrete",
    title: "Lembrete de pagamento",
    description: "5 sócios com pagamento pendente",
    time: "há 5 horas",
    icon: Clock,
    iconColor: "text-red-600",
  },
]

export function RecentActivities() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Atividades Recentes</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px]">
          <div className="space-y-4">
            {activities.map((activity) => (
              <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg border">
                <div className={`p-2 rounded-full bg-muted ${activity.iconColor}`}>
                  <activity.icon className="h-4 w-4" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium">{activity.title}</h4>
                    <span className="text-xs text-muted-foreground">{activity.time}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {activity.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}