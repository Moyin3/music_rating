

const getReviews = async({url}) =>{
        let result = {"status": null, "json": null};
        let getRequest = {method: "GET", credentials: "include", headers:{ "Content-Type": "application/json"}};
        console.log("Is this function being called")
        try{
            console.log("fetch url", url)
            const response = await fetch(url, getRequest);
            console.log("Response", response)
            if (response.status === 200){
                result = {"status": "success", "json": await response.json()};
            }
        }
        catch(error){
            console.error("Error:", error)
            result = {"status": `error: ${error}`, "json": null}
        }
        console.log("what is returning", result)
        return result
    }

export default getReviews;