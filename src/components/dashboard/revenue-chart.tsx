"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const data = [
  { month: "Jan", revenue: 4000, expenses: 2400 },
  { month: "Fev", revenue: 3000, expenses: 1398 },
  { month: "Mar", revenue: 9800, expenses: 2000 },
  { month: "Abr", revenue: 3908, expenses: 2780 },
  { month: "Mai", revenue: 4800, expenses: 1890 },
  { month: "Jun", revenue: 3800, expenses: 2390 },
]

export function RevenueChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Receita vs Despesas</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="revenue" fill="#10b981" name="Receita" />
            <Bar dataKey="expenses" fill="#ef4444" name="Despesas" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}