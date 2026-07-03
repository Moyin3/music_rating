const LoginCheck = async (event) => {
    try{
        const response = await fetch("http://127.0.0.1:8000/api/dj-rest-auth/user/",{
            method: "GET",
            credentials: "include",
        }
        );
        if (response.ok) {
            const user = await response.json();
        }
    } catch{
        user = null;
    }
    return (
        user
    )
}

export default LoginCheck;