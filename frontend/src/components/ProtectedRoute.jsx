import { Navigate, Outlet, useLocation } from "react-router";

const ProtectedRoute = (props) =>{
const location = useLocation();
const Data = location.state;
console.log("Is it getting here?", Data)
    return (
        props.isAuthenticated ?
        <Outlet /> : <Navigate to = "/login" state = {{priorData: {location, Data}}}  />
    )
}

export default ProtectedRoute;