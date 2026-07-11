import { Link } from 'react-router';

const CreateRatingButton = ({name, type, spotify_id}) => {
    console.log("Data being sent", {name, type, spotify_id});
    return(
        <>
        <Link to= "/rating" state =  {{"data": {name, type, spotify_id}}}>
        <button>Create Rating</button>
        </Link>
        </>
    )
}

export default CreateRatingButton;