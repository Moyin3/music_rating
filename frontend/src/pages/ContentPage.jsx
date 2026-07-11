import NavigationBar from "../components/Navigationbar";
import { useLocation } from "react-router";
import CreateRatingButton from "../components/CreateRatingButton";

const ContentPage = () => {
    let metadata = useLocation().state;
    return(
        <>
        <NavigationBar />
        <h1>{metadata.data.name}</h1>
        <CreateRatingButton type={metadata.data.type} name = {metadata.data.name} spotify_id={metadata.data.id} />
        </>
    )
}

export default ContentPage;