import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import UploadVideo from './UploadVideo';
import video from "./assets/background.mp4";



function PostMatch() {
    return(
        <>
            <div className='flex flex-col h-screen justify-center items-center'>
            <video autoPlay muted loop className='fixed top-0 left-0 w-full h-full object-cover z-[-2]' > <source src={video} type='video/mp4' /> </video>

                <UploadVideo />
            </div>
        </>
    );
}

export default PostMatch;
