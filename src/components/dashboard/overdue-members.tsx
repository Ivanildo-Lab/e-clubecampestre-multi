"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  AlertTriangle,
  Mail,
  MessageSquare,
  MoreHorizontal
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const overdueMembers = [
  {
    id: 1,
    name: "Carlos Alberto",
    email: "carlos@email.com",
    phone: "(11) 99999-8888",
    overdueAmount: 150.00,
    overdueDays: 15,
    category: "Titular",
  },
  {
    id: 2,
    name: "Ana Paula",
    email: "ana@email.com",
    phone: "(11) 99999-7777",
    overdueAmount: 300.00,
    overdueDays: 30,
    category: "Titular",
  },
  {
    id: 3,
    name: "Roberto Silva",
    email: "roberto@email.com",
    phone: "(11) 99999-6666",
    overdueAmount: 150.00,
    overdueDays: 45,
    category: "Dependente",
  },
  {
    id: 4,
    name: "Fernanda Costa",
    email: "fernanda@email.com",
    phone: "(11) 99999-5555",
    overdueAmount: 450.00,
    overdueDays: 60,
    category: "Titular",
  },
]

export function OverdueMembers() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          Sócios Inadimplentes
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px]">
          <div className="space-y-4">
            {overdueMembers.map((member) => (
              <div key={member.id} className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback>
                      {member.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h4 className="text-sm font-medium">{member.name}</h4>
                    <p className="text-xs text-muted-foreground">
                      {member.category} • {member.overdueDays} dias atrasado
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-right">
                    <p className="text-sm font-medium text-red-600">
                      R$ {member.overdueAmount.toFixed(2)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {member.overdueDays} dias
                    </p>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>
                        <Mail className="h-4 w-4 mr-2" />
                        Enviar email
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <MessageSquare className="h-4 w-4 mr-2" />
                        Enviar WhatsApp
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}