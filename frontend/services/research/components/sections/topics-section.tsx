import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function TopicsSection({ topics }: { topics: string[] }) {
  if (!topics || topics.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>المواضيع الرئيسية</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-2">
        {topics.map((topic) => (
          <Badge key={topic} variant="secondary" className="font-normal">
            {topic}
          </Badge>
        ))}
      </CardContent>
    </Card>
  );
}
