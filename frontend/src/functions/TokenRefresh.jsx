const TokenRefresh = async (event) => {
    let access_token = null;
    try {
        const response = await fetch("http://127.0.0.1:8000/api/dj-rest-auth/token/refresh",{
            method: "POST",
            credentials: "include",

        }
        );
        if (response.ok){
            access_token = await response.json();
        }
    } catch{
        access_token = null;
    }
    return(
        access_token
    )
}

export default TokenRefresh;