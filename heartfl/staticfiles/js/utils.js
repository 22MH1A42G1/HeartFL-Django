/**
 * HeartFL - Utilities & Helper Functions
 * Reusable utility functions for common operations
 */

// ============================================================================
// DOM UTILITIES
// ============================================================================

const DOM = {
    /**
     * Query selector shortcut
     */
    select: (selector) => document.querySelector(selector),

    /**
     * Query all selector shortcut
     */
    selectAll: (selector) => document.querySelectorAll(selector),

    /**
     * Create element with classes
     */
    createElement: (tag, className = '', innerHTML = '') => {
        const el = document.createElement(tag);
        if (className) el.className = className;
        if (innerHTML) el.innerHTML = innerHTML;
        return el;
    },

    /**
     * Add class to element
     */
    addClass: (el, className) => el.classList.add(className),

    /**
     * Remove class from element
     */
    removeClass: (el, className) => el.classList.remove(className),

    /**
     * Toggle class
     */
    toggleClass: (el, className) => el.classList.toggle(className),

    /**
     * Has class
     */
    hasClass: (el, className) => el.classList.contains(className),

    /**
     * Get element by ID
     */
    byId: (id) => document.getElementById(id),

    /**
     * Set multiple attributes
     */
    setAttrs: (el, attrs) => {
        Object.entries(attrs).forEach(([key, value]) => {
            el.setAttribute(key, value);
        });
    },

    /**
     * Get attribute
     */
    getAttr: (el, attr) => el.getAttribute(attr),

    /**
     * Set text content
     */
    setText: (el, text) => { el.textContent = text; },

    /**
     * Set HTML content
     */
    setHTML: (el, html) => { el.innerHTML = html; },

    /**
     * Get text content
     */
    getText: (el) => el.textContent,

    /**
     * Show element
     */
    show: (el) => { el.style.display = ''; },

    /**
     * Hide element
     */
    hide: (el) => { el.style.display = 'none'; },

    /**
     * Toggle visibility
     */
    toggle: (el) => { el.style.display = el.style.display === 'none' ? '' : 'none'; },

    /**
     * Remove element
     */
    remove: (el) => el.remove(),

    /**
     * Append child
     */
    append: (parent, child) => parent.appendChild(child),

    /**
     * Prepend child
     */
    prepend: (parent, child) => parent.insertBefore(child, parent.firstChild),

    /**
     * Add event listener
     */
    on: (el, event, handler) => el.addEventListener(event, handler),

    /**
     * Remove event listener
     */
    off: (el, event, handler) => el.removeEventListener(event, handler),

    /**
     * Trigger event
     */
    trigger: (el, event) => el.dispatchEvent(new Event(event, { bubbles: true }))
};

// ============================================================================
// STRING UTILITIES
// ============================================================================

const STRING = {
    /**
     * Capitalize string
     */
    capitalize: (str) => str.charAt(0).toUpperCase() + str.slice(1),

    /**
     * Lowercase first char
     */
    uncapitalize: (str) => str.charAt(0).toLowerCase() + str.slice(1),

    /**
     * Convert to title case
     */
    titleCase: (str) => {
        return str.replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
    },

    /**
     * Convert to snake_case
     */
    snakeCase: (str) => {
        return str.match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
            .map(x => x.toLowerCase())
            .join('_');
    },

    /**
     * Convert to camelCase
     */
    camelCase: (str) => {
        return str.replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => 
            index === 0 ? word.toLowerCase() : word.toUpperCase()
        ).replace(/\s+/g, '');
    },

    /**
     * Truncate string
     */
    truncate: (str, length, suffix = '...') => {
        return str.length > length ? str.slice(0, length) + suffix : str;
    },

    /**
     * Repeat string
     */
    repeat: (str, count) => str.repeat(count),

    /**
     * Reverse string
     */
    reverse: (str) => str.split('').reverse().join(''),

    /**
     * Is email
     */
    isEmail: (str) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str),

    /**
     * Is URL
     */
    isURL: (str) => {
        try {
            new URL(str);
            return true;
        } catch {
            return false;
        }
    },

    /**
     * Remove special characters
     */
    removeSpecial: (str) => str.replace(/[^\w\s]/gi, ''),

    /**
     * Escape HTML
     */
    escapeHTML: (str) => {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    /**
     * Generate random string
     */
    random: (length = 8) => {
        return Math.random().toString(36).substring(2, 2 + length);
    }
};

// ============================================================================
// ARRAY UTILITIES
// ============================================================================

const ARRAY = {
    /**
     * Get unique values
     */
    unique: (arr) => [...new Set(arr)],

    /**
     * Flatten array
     */
    flatten: (arr) => arr.reduce((flat, item) => flat.concat(Array.isArray(item) ? ARRAY.flatten(item) : item), []),

    /**
     * Shuffle array
     */
    shuffle: (arr) => {
        const copy = [...arr];
        for (let i = copy.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [copy[i], copy[j]] = [copy[j], copy[i]];
        }
        return copy;
    },

    /**
     * Chunk array
     */
    chunk: (arr, size) => {
        const chunks = [];
        for (let i = 0; i < arr.length; i += size) {
            chunks.push(arr.slice(i, i + size));
        }
        return chunks;
    },

    /**
     * Group by property
     */
    groupBy: (arr, prop) => {
        return arr.reduce((groups, item) => {
            const key = item[prop];
            groups[key] = (groups[key] || []).concat(item);
            return groups;
        }, {});
    },

    /**
     * Get max value
     */
    max: (arr) => Math.max(...arr),

    /**
     * Get min value
     */
    min: (arr) => Math.min(...arr),

    /**
     * Sum array
     */
    sum: (arr) => arr.reduce((a, b) => a + b, 0),

    /**
     * Average
     */
    avg: (arr) => ARRAY.sum(arr) / arr.length,

    /**
     * Remove duplicates while preserving order
     */
    deduplicate: (arr) => {
        const seen = new Set();
        return arr.filter(item => {
            if (seen.has(item)) return false;
            seen.add(item);
            return true;
        });
    }
};

// ============================================================================
// OBJECT UTILITIES
// ============================================================================

const OBJ = {
    /**
     * Get nested value
     */
    get: (obj, path) => {
        return path.split('.').reduce((current, prop) => current?.[prop], obj);
    },

    /**
     * Set nested value
     */
    set: (obj, path, value) => {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((o, key) => o[key] = o[key] || {}, obj);
        target[lastKey] = value;
        return obj;
    },

    /**
     * Deep clone
     */
    clone: (obj) => JSON.parse(JSON.stringify(obj)),

    /**
     * Merge objects
     */
    merge: (target, source) => {
        for (let key in source) {
            if (source.hasOwnProperty(key)) {
                target[key] = source[key];
            }
        }
        return target;
    },

    /**
     * Get keys
     */
    keys: (obj) => Object.keys(obj),

    /**
     * Get values
     */
    values: (obj) => Object.values(obj),

    /**
     * Get entries
     */
    entries: (obj) => Object.entries(obj),

    /**
     * Filter keys
     */
    filterKeys: (obj, predicate) => {
        const result = {};
        for (let key in obj) {
            if (predicate(key)) {
                result[key] = obj[key];
            }
        }
        return result;
    }
};

// ============================================================================
// NUMBER UTILITIES
// ============================================================================

const NUM = {
    /**
     * Format number with commas
     */
    format: (num) => {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    /**
     * Format as currency
     */
    currency: (num, currency = 'USD') => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(num);
    },

    /**
     * Format as percentage
     */
    percent: (num, decimals = 2) => {
        return (num * 100).toFixed(decimals) + '%';
    },

    /**
     * Round to decimal places
     */
    round: (num, decimals = 0) => {
        const factor = Math.pow(10, decimals);
        return Math.round(num * factor) / factor;
    },

    /**
     * Clamp number
     */
    clamp: (num, min, max) => Math.min(Math.max(num, min), max),

    /**
     * Random number
     */
    random: (min = 0, max = 1) => {
        return Math.random() * (max - min) + min;
    }
};

// ============================================================================
// DATE UTILITIES
// ============================================================================

const DATE = {
    /**
     * Format date
     */
    format: (date, format = 'MM/DD/YYYY') => {
        const d = new Date(date);
        const map = {
            MM: String(d.getMonth() + 1).padStart(2, '0'),
            DD: String(d.getDate()).padStart(2, '0'),
            YYYY: d.getFullYear()
        };
        return format.replace(/MM|DD|YYYY/g, matched => map[matched]);
    },

    /**
     * Get relative time (e.g., "2 hours ago")
     */
    relative: (date) => {
        const d = new Date(date);
        const seconds = Math.floor((new Date() - d) / 1000);
        
        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60
        };

        for (const [name, value] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / value);
            if (interval >= 1) {
                return interval === 1 ? `1 ${name} ago` : `${interval} ${name}s ago`;
            }
        }
        return 'just now';
    },

    /**
     * Is date in past
     */
    isPast: (date) => new Date(date) < new Date(),

    /**
     * Is date in future
     */
    isFuture: (date) => new Date(date) > new Date()
};

// ============================================================================
// LOCAL STORAGE UTILITIES
// ============================================================================

const STORAGE = {
    /**
     * Set item
     */
    set: (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
    },

    /**
     * Get item
     */
    get: (key) => {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },

    /**
     * Remove item
     */
    remove: (key) => localStorage.removeItem(key),

    /**
     * Clear all
     */
    clear: () => localStorage.clear(),

    /**
     * Has key
     */
    has: (key) => localStorage.getItem(key) !== null
};

// ============================================================================
// PROMISE UTILITIES
// ============================================================================

/**
 * Timeout promise
 */
function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry promise
 */
async function retry(fn, maxAttempts = 3, delay = 1000) {
    for (let i = 0; i < maxAttempts; i++) {
        try {
            return await fn();
        } catch (error) {
            if (i === maxAttempts - 1) throw error;
            await timeout(delay);
        }
    }
}

/**
 * Race with timeout
 */
function raceTimeout(promise, ms) {
    return Promise.race([
        promise,
        new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Timeout')), ms)
        )
    ]);
}

// ============================================================================
// EVENT UTILITIES
// ============================================================================

const EVENT = {
    /**
     * Emit custom event
     */
    emit: (eventName, detail = {}) => {
        document.dispatchEvent(new CustomEvent(eventName, { detail }));
    },

    /**
     * Listen to custom event
     */
    on: (eventName, callback) => {
        document.addEventListener(eventName, (e) => callback(e.detail));
    },

    /**
     * Listen once
     */
    once: (eventName, callback) => {
        const listener = (e) => {
            callback(e.detail);
            document.removeEventListener(eventName, listener);
        };
        document.addEventListener(eventName, listener);
    }
};

// ============================================================================
// LOGGER UTILITY
// ============================================================================

const LOG = {
    /**
     * Log with prefix
     */
    info: (message, data = null) => {
        console.log(`[INFO] ${message}`, data || '');
    },

    /**
     * Log warning
     */
    warn: (message, data = null) => {
        console.warn(`[WARN] ${message}`, data || '');
    },

    /**
     * Log error
     */
    error: (message, data = null) => {
        console.error(`[ERROR] ${message}`, data || '');
    },

    /**
     * Log debug
     */
    debug: (message, data = null) => {
        console.debug(`[DEBUG] ${message}`, data || '');
    }
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('HeartFL Utilities Loaded');
    LOG.info('Utility modules available: DOM, STRING, ARRAY, OBJ, NUM, DATE, STORAGE, EVENT, LOG');
});

// ============================================================================
// EXPORT FOR GLOBAL USE
// ============================================================================

window.DOM = DOM;
window.STRING = STRING;
window.ARRAY = ARRAY;
window.OBJ = OBJ;
window.NUM = NUM;
window.DATE = DATE;
window.STORAGE = STORAGE;
window.EVENT = EVENT;
window.LOG = LOG;
window.timeout = timeout;
window.retry = retry;
window.raceTimeout = raceTimeout;
