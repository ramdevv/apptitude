import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {  useNavigate } from "react-router-dom"
import { useState } from "react"
import { useEffect } from "react"
import { useRequest } from "./request_button"



export function Register() {
  const[email, setEmail] = useState("");
  const[name, setName] = useState("");
  const[password, setPassword] = useState("");
  const navigate = useNavigate();


  // to send the request to the backend with the useRequest hook 
  const request = useRequest({
    url: "http://localhost:8000/auth/register",
    body:{
            "name": name,
            "email":email,
            "password":password
        }
  });
  useEffect(() => {
      if (request.succesfull === true){
          console.log("the login is succesfull");
          navigate("/")

      }else{
          console.log("login is not succesfull");
      }
  })

  // handling the response of the request
  const handleResponse = async (e: React.FormEvent) => {
      e.preventDefault();  // this prevents the page to defalut reload 
      try{
          const res = await request.sendRequest();
      } 
      catch(error){
          console.log("message: ", error);
      }


  }
  return (
          <Card className="w-full max-w-sm">
              <CardHeader>
                   <Button
                              type="button"
                              variant="outline"
                              className="w-full"
                              onClick={() => navigate("/Register")}
                          >
                              Go to Register
                          </Button>
                  <CardTitle>Create Account</CardTitle>
                  <CardDescription>
                      Fill in the details to login.
                  </CardDescription>
              </CardHeader>
              <CardContent>
                  <form onSubmit={handleResponse}>
                      <div className="flex flex-col gap-6">
                          <div className="grid gap-2">
                              <Label htmlFor="name">Name</Label>
                              <Input
                                  id="name"
                                  type="text"
                                  placeholder="Your name"
                                  value={name}
                                  onChange={(e) => setName(e.target.value)}
                                  required
                              />
                          </div>
                          <div className="grid gap-2">
                              <Label htmlFor="email">Email</Label>
                              <Input
                                  id="email"
                                  type="email"
                                  placeholder="m@example.com"
                                  value={email}
                                  onChange={(e) => setEmail(e.target.value)}
                                  required
                              />
                          </div>
                          <div className="grid gap-2">
                              <Label htmlFor="password">Password</Label>
                              <Input
                                  id="password"
                                  type="password"
                                  value={password}
                                  onChange={(e) => setPassword(e.target.value)}
                                  required
                              />
                          </div>
                          {request.error && <p className="text-red-500">{request.error}</p>}
                      </div>
                      <CardFooter className="flex-col gap-2 mt-4">
                          <Button type="submit" className="w-full" disabled={request.loading}>
                              {request.loading ? "LogingIn…" : "Login"}
                          </Button>
                  
                      </CardFooter>
                  </form>
              </CardContent>
          </Card>
      );



  
}
