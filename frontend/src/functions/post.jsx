import TokenRefresh from "./TokenRefresh";

const post = async ({url, data}) => {
    let result = {"status": null, "json": null};
    let postRequest = {method: "POST", credentials: "include", headers:{ "Content-Type": "application/json"}, body:JSON.stringify(data)}
    try{
        const response = await fetch(url, postRequest);
        if (response.status === 401){
                let refreshtoken = await TokenRefresh();

                if (refreshtoken != null){
                const retryResponse = await fetch(url, postRequest);
                 if (retryResponse.status === 201){
            result = {"status": "success", "json": await retryResponse.json()}
        }else{
            result = {"status": "error: request failed", "json": null};
        }
                }
                else{
                    result = {"status": "need login", "json": null}
                }
                //Need to handle status codes better
            }else if (response.status === 201){
                result = {"status": "success", "json": await response.json()}
            }else if (response.status ===200){
                result = {"status": "success", "json": await response.json()}
            }else{
                result = {"status": "error: request failed", "json": null}
            }
    }catch(error){
        console.error("Error:", error);
        result = {"status": `error: ${error}`, "json": null}
    }
    return(
        result
    )
}

export default post;