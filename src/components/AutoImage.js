import React, {useState} from 'react';
import '@site/src/css/AutoImage.css';

const AutoImage = ({src}) => {
    const [isFullScreen, setIsFullScreen] = useState(false);

    return (
        <div className="image-container">
            {isFullScreen && (
                <div className="full-screen" onClick={() => setIsFullScreen(false)}>
                    <img
                        src={src}
                        alt="Full Screen Image"
                    />
                </div>
            )}
            <img
                src={src}
                alt="Full Screen Image"
                style={{
                    cursor: "zoom-in",
                    visibility: isFullScreen ? 'hidden' : 'visible',
                }}
                onClick={(e) => setIsFullScreen(!isFullScreen)}
            />
        </div>
    );
};

export default AutoImage;
