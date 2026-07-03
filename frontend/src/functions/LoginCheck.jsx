const LoginCheck = async (event) => {
    let user = null;
    try{
        const response = await fetch("http://127.0.0.1:8000/api/dj-rest-auth/user/",{
            method: "GET",
            credentials: "include",
        }
        );
        if (response.ok) {
            user = await response.json();
        }
    } catch {
        user = null;
    }
    return (
        user
    )
}

export default LoginCheck;