import AuthContext from "./AuthContext";
import { useState } from "react";

function AuthProvider({children}){
    const [user, setUser] = useState(null);

    const value = { user, setUser };
    console.log(user);
    return(
        <AuthContext.Provider value = {value}>
            {children}
        </AuthContext.Provider>
    );
}

export default AuthProvider;